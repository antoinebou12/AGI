from commands.command import BaseCommand
from functions import browse


class WebsiteCommand(BaseCommand):
    def execute(self, argument):
        self.browse_website(argument)

    def browse_website(self, url, argument):
        """Browse a website and return the summary and links"""
        summary = self.get_text_summary(url, argument)
        links = self.get_hyperlinks(url)

        # Limit links to 5
        if len(links) > 5:
            links = links[:5]

        return f"""Website Content Summary: {summary}\n\nLinks: {links}"""

    def get_text_summary(self, url, argument):
        """Return the results of a google search"""
        text = browse.scrape_text(url)
        summary = browse.summarize_text(text, argument)
        return f""" "Result" : {summary}"""

    def get_hyperlinks(self, url):
        """Return the results of a google search"""
        return browse.scrape_links(url)
