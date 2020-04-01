from django.test import TestCase

from deferred_save.models import Blog, Post, Comment, Tag, Comment_Tag

NUM_BLOGS = 10
NUM_POSTS = 10
NUM_COMMENTS = 10
NUM_TAGS = 3

TAGS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class TestBulkSaveAll(TestCase):
    def setUp(self):
        self.tags = []
        for tag in TAGS:
            self.tags.append(Tag.objects.create(name=tag))

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
                post.name=f"post {i}{j}"
                post.blog = blog
                posts.append(post)
                for k in range(NUM_COMMENTS):
                    comment = Comment()
                    comment.name=f"comment {i}{j}{k}"
                    comment.post = post
                    comments.append(comment)

                    for l in range(NUM_TAGS):
                        comment_tag = Comment_Tag(tag=self.tags[l % len(TAGS)], comment=comment)
                        comment_tags.append(comment_tag)

        self.assertEqual(NUM_BLOGS, len(blogs))
        self.assertEqual(NUM_BLOGS*NUM_POSTS, len(posts))
        self.assertEqual(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS, len(comments))
        self.assertEqual(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS*NUM_TAGS, len(comment_tags))

        with self.assertNumQueries(4):
            Blog.objects.bulk_create(blogs)
            Post.bulk_manager.bulk_create(posts)
            Comment.bulk_manager.bulk_create(comments)
            Comment_Tag.bulk_manager.bulk_create(comment_tags)

        self.assertEqual(NUM_BLOGS, Blog.objects.count())
        self.assertEqual(NUM_BLOGS*NUM_POSTS, Post.objects.count())
        self.assertEqual(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS, Comment.objects.count())
        self.assertEqual(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS*NUM_TAGS, Comment_Tag.objects.count())

    def test_bulk_save_all_bulk_without_nesting(self):
        """
        Creates the same number of objects as the test method above but no nesting so
        :return:
        """
        blogs = []
        posts = []
        comments = []
        comment_tags = []
        for i in range(NUM_BLOGS):
            blog = Blog(name=f"blog {i}")
            blogs.append(blog)
        Blog.objects.bulk_create(blogs)

        for j in range(NUM_BLOGS*NUM_POSTS):
            post = Post()
            post.name=f"post {j}"
            post.blog = blogs[0]
            posts.append(post)
        Post.bulk_manager.bulk_create(posts)

        for k in range(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS):
            comment = Comment()
            comment.name=f"comment {k}"
            comment.post = posts[0]
            comments.append(comment)
            for l in range(NUM_TAGS):
                comment_tag = Comment_Tag(tag=self.tags[l % len(TAGS)], comment=comment)
                comment_tags.append(comment_tag)

        Comment.bulk_manager.bulk_create(comments)
        Comment_Tag.bulk_manager.bulk_create(comment_tags)

        self.assertEqual(NUM_BLOGS, Blog.objects.count())
        self.assertEqual(NUM_BLOGS*NUM_POSTS, Post.objects.count())
        self.assertEqual(NUM_BLOGS*NUM_POSTS*NUM_COMMENTS, Comment.objects.count())
        self.assertEqual(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS * NUM_TAGS, Comment_Tag.objects.count())

    def test_bulk_save_all_without_bulk(self):
        """
        No bulk operations, this is very slow.
        """
        for i in range(NUM_BLOGS):
            blog = Blog(name=f"blog {i}")
            blog.save()
            for j in range(NUM_POSTS):
                post = Post()
                post.name=f"post {i}{j}"
                post.blog = blog
                post.save()
                for k in range(NUM_COMMENTS):
                    comment = Comment()
                    comment.name=f"comment {i}{j}{k}"
                    comment.post = post
                    comment.save()
                    for l in range(NUM_TAGS):
                        comment.tags.add(self.tags[l % len(TAGS)])

        self.assertEqual(NUM_BLOGS, Blog.objects.count())
        self.assertEqual(NUM_BLOGS * NUM_POSTS, Post.objects.count())
        self.assertEqual(NUM_BLOGS * NUM_POSTS * NUM_COMMENTS, Comment.objects.count())


