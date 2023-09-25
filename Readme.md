# Circle RSS
A personal one-offish project to create an RSS feed of Circle.so posts to be included on a Squarespace page

Circle.so doesn't currently offer an RSS feed of its forum posts. I wanted to be able to tease the community blog posts, which is member-only content, on the public website.

I also wanted the public Announcements post content to be re-posted on the public website. It is better for content creators to use the Circle.so interface to create announcements over the Squarespace blog post interface since Cirle.so is designed for UGC wherease Squarespace requires a backend interface.

There are two scripts (with redundant code I know). They are being run by pipedream on a scheduled trigger.
The first script is for the Blog space and the second is for the Announcements space.

The resultant xml files are stored on a publicly readable AWS S3 bucket which avoids CORS issues on Squarespace.

On the Squarespace side, I use a code block to insert the html which contains some (basic atm) style elements and javascrpt to read the xml from the S3 url and render it on the Squarespace page.

The script uses a ~/.ola/config.ini file to store credentials and urls. Within pipedream, it uses a data store.

This is a quick and dirty script. Not optimized and no error handling. It performs the task intended to my satisfaction.