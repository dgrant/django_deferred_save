from django.test import TestCase

from deferred_save.models import Blog, Post, Comment, Tag, Comment_Tag

NUM_BLOGS = 5
NUM_POSTS = 5
NUM_COMMENTS = 5
NUM_TAGS = 3

TAGS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class TestBulkSaveAll(TestCase):
    def setUp(self):
        self.tags = []
        for tag in TAGS:
            self.tags.append(Tag(name=tag))
        Tag.objects.bulk_create(self.tags)

    def test_bulk_save_all_bulk(self):
        blogs = []
        posts = []
        comments = []
        comment_tags = []
        for i in range(NUM_BLOGS):
            blog = Blog(name=f"blog {i}")
            blogs.append(blog)
            for j in range(NUM_POSTS):
                post = Post()
                post.name = f"post {i}{j}"
                post.blog = blog
                posts.append(post)

                # The 0th, 5th, 10th, etc... posts will be parent posts.
                # the 1st-4th, 6th-9th, etc... will have parent post equal to the previous parent
                for k in range(NUM_COMMENTS):
                    comment = Comment()
                    comment.name = f"comment {i}{j}{k}"
                    comment.post = post
                    comments.append(comment)
                    is_parent = k % 5 == 0
                    if not is_parent:
                        comment.parent = comments[-1 - (k % 5)]
                    for l in range(NUM_TAGS):
                        comment_tag = Comment_Tag(
                            tag=self.tags[l % len(TAGS)], comment=comment
                        )
                        comment_tags.append(comment_tag)

        with self.assertNumQueries(5):
            Blog.objects.bulk_create(blogs)
            Post.bulk_manager.bulk_create(posts)
            # This takes 2 queries due to the self/parent reference
            Comment.bulk_manager.bulk_create(comments)
            Comment_Tag.bulk_manager.bulk_create(comment_tags)

        self._check_entity_counts()

    def test_bulk_save_all_bulk_without_nesting(self):
        """
        Creates the same number of objects as the test method above but no nesting so
        :return:
        """
        blogs = []
        posts = []
        comments = []
        comment_tags = []
        with self.assertNumQueries(6):
            for i in range(NUM_BLOGS):
                blog = Blog(name=f"blog {i}")
                blogs.append(blog)
            Blog.objects.bulk_create(blogs)

            for j in range(NUM_BLOGS * NUM_POSTS):
                post = Post()
                post.name = f"post {j}"
                post.blog = blogs[0]
                posts.append(post)
            Post.bulk_manager.bulk_create(posts)

            for k in range(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS):
                comment = Comment()
                comment.name = f"comment {k}"
                comment.post = posts[0]
                comments.append(comment)
                for l in range(NUM_TAGS):
                    comment_tag = Comment_Tag(
                        tag=self.tags[l % len(TAGS)], comment=comment
                    )
                    comment_tags.append(comment_tag)

            Comment.bulk_manager.bulk_create(comments)

            comments_to_update = []
            comments = list(Comment.objects.all())
            for k, comment in enumerate(comments):
                is_parent = k % 5 == 0
                if not is_parent:
                    comment.parent = comments[-1 - (k % 5)]
                    comments_to_update.append(comment)

            Comment.objects.bulk_update(comments_to_update, ["parent"])

            Comment_Tag.bulk_manager.bulk_create(comment_tags)

        self._check_entity_counts()

    def test_bulk_save_all_without_bulk(self):
        """
        No bulk operations, this is very slow.
        """
        num_expected_queries = (
            NUM_BLOGS
            + (NUM_BLOGS * NUM_POSTS)
            + (NUM_BLOGS * NUM_POSTS * NUM_COMMENTS)
            + (NUM_BLOGS * NUM_POSTS * NUM_COMMENTS * NUM_TAGS * 2)
        )
        with self.assertNumQueries(num_expected_queries):
            for i in range(NUM_BLOGS):
                blog = Blog(name=f"blog {i}")
                blog.save()
                for j in range(NUM_POSTS):
                    post = Post()
                    post.name = f"post {i} {j}"
                    post.blog = blog
                    post.save()
                    comments = []
                    for k in range(NUM_COMMENTS):
                        comment = Comment()
                        comment.name = f"comment {i}{j}{k}"
                        comment.post = post
                        comments.append(comment)
                        is_parent = k % 5 == 0
                        if not is_parent:
                            comment.parent = comments[-1 - (k % 5)]
                        comment.save()
                        for l in range(NUM_TAGS):
                            comment.tags.add(self.tags[l % len(TAGS)])

        self._check_entity_counts()

    def _check_entity_counts(self):
        self.assertEqual(NUM_BLOGS, Blog.objects.count())
        self.assertEqual(NUM_BLOGS * NUM_POSTS, Post.objects.count())
        self.assertEqual(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS, Comment.objects.count())
        self.assertEqual(
            NUM_BLOGS * NUM_POSTS * NUM_COMMENTS * NUM_TAGS, Comment_Tag.objects.count()
        )
        # Check that 1/5th of all posts have is parent set to something
        self.assertEqual(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS * 1 / 5, Comment.objects.filter(parent__isnull=True).count())
        # Check that 4/5th of all posts have is parent set to something
        self.assertEqual(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS * 4 / 5, Comment.objects.filter(parent__isnull=False).count())
