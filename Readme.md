# Circle RSS

## There are two functions available here. 

* The first creates an RSS Feed from your Circle.so space and provides an html widget to display the RSS feed on a website that is external to your Circle.so community.
* The second uses an RSS Feed external to your Circle.so community to make posts to a Circle.so space
A personal one-offish project to create an RSS feed of Circle.so posts to be included on a Squarespace page

Both functions require some variables to be set either via a config file or via environment variables. They are:

* circle_token = `Token <your token>`
* community_id = `<target circle.so community id>`
* space_id = `<target circle.so space id>`

## CircleRSS Outgoing

Circle.so doesn't currently offer an RSS feed of its forum posts. I wanted to be able to tease the community blog posts, which is member-only content, on the public website.

I also wanted the public Announcements post content to be re-posted on the public website. It is better for content creators to use the Circle.so interface to create announcements over the Squarespace blog post interface since Cirle.so is designed for UGC wherease Squarespace requires a backend interface.

There are two scripts (with redundant code I know). They are being run by pipedream on a scheduled trigger.
The first script is for the Blog space and the second is for the Announcements space.

The resultant xml files are stored on a publicly readable AWS S3 bucket which avoids CORS issues on Squarespace.

On the Squarespace side, I use a code block to insert the html which contains some (basic atm) style elements and javascrpt to read the xml from the S3 url and render it on the Squarespace page.

The script uses a ~/.ola/config.ini file to store credentials and urls. Within pipedream, it uses environment variables.

This is a quick and dirty script. Not optimized and no error handling. It performs the task intended to my satisfaction.

## CircleRSS Incoming

We have a blog space in our circle community where our authors can share their personal blog posts to drive traffic from Opus to their personal blogs. Rather than having our authors remember to cross-post a teaser of their blog posts to Opus, I wanted to create an automated way to share these posts.

This script also runs on pipedream on a schedule. It takes a list of rss feeds and creates a post teaser within the blog space of our circle community from the most recent item in the rss feed. It checks to make sure the post has not already been made so that we don't have duplicate posts. Since there is no consistency between the author blog email and the circle.so community email, the script requires the email of the circle.so community post author to be associated with the rss feed like this:

`"https://example.feed.com/feed": "member_author@email.com",`
