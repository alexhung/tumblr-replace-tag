import argparse

import pytumblr

DEFAULT_PAGE_SIZE = 20


class TumblrReplaceTags(object):
    def __init__(self, consumer_key, consumer_secret, blog_name,
                 old_tag, new_tag):

        self.blog_name = blog_name
        self.old_tag = old_tag
        self.new_tag = new_tag
        self.posts_processed = 0

        self.tumblr_client = pytumblr.TumblrRestClient(
            consumer_key, consumer_secret)

    def execute(self):
        print(self.blog_name)

        params = {
            'tag': self.old_tag,
            'offset': 0,
        }
        posts = self.tumblr_client.posts(self.blog_name, **params)
        if 'meta' in posts and posts['meta']['status'] != 200:
            print('Error getting posts: {}'.format(posts['meta']['msg']))
            return

        total_posts = posts['total_posts']

        pages, remainder = divmod(total_posts, DEFAULT_PAGE_SIZE)
        if pages == 0:
            pages += 1
        else:
            if remainder > 0:
                pages += 1

        for i in range(0, pages):
            for post in posts['posts']:
                self._update_post_tags(post)

            params = {
                'tag': self.old_tag,
                'offset': i * DEFAULT_PAGE_SIZE
            }
            posts = self.tumblr_client.posts(self.blog_name, **params)
            if 'meta' in posts and posts['meta']['status'] != 200:
                print('Error getting posts: {}'.format(posts['meta']['msg']))
                continue

        print('Saved {} posts out of {}'.format(self.posts_processed,
                                                total_posts))

    def _update_post_tags(self, post):
        print('Saving post: {}'.format(post['id']))

        tags = post['tags']
        tags.remove(self.old_tag)
        tags.append(self.new_tag)
        self.tumblr_client.edit_post(self.blog_name, id=post['id'], tags=tags)

        self.posts_processed += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('consumer_key', metavar='consumer_key', type=str,
                        help='Tumblr API consumer key')
    parser.add_argument('consumer_secret', metavar='consumer_secret',
                        type=str, help='Tumblr API consumer secret')
    parser.add_argument('blog_name', metavar='blog_name', type=str,
                        help='Tumblr blog name')
    parser.add_argument('old_tag', metavar='old_tag',
                        type=str, help='Existing tag')
    parser.add_argument('new_tag', metavar='new_tag',
                        type=str, help='New tag')

    args = parser.parse_args()

    backup = TumblrReplaceTags(**vars(args))
    backup.execute()
