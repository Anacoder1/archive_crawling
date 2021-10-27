"""Code is from the news-please source code and hasn't been modified."""

# -*- coding: utf-8 -*-
import re
from lxml import html  # nosec
# import sys

# to improve performance, regex statements are compiled only once per module
re_newline_spc = re.compile(r'(?<=\n)( )+')
re_starting_whitespc = re.compile(r'^[ \t\n\r\f]*')
re_multi_spc_tab = re.compile(r'[ \t]+(?=([ \t]))')
re_double_newline = re.compile(r'[ \n]+(?=(\n))')
re_ending_spc_newline = re.compile(r'[ \n]*$')


class Cleaner:
    """
    The Cleaner-Class tries to get the raw extracted text of the extractors
    in a comparable format. For this it deletes unnecessary whitespaces
    or in case of readability html-tags which are still in the extracted
    text.
    """
    def delete_tags(self, arg):  # pylint: disable=no-self-use
        """
        Removes html-tags from extracted data.
        :param arg: A string, the string which shall be cleaned
        :return: A string, the cleaned string
        """

        if arg:
            raw = html.fromstring(arg)
            return raw.text_content().strip()

        return arg

    def delete_whitespaces(self, arg):  # pylint: disable=no-self-use
        """
        Removes newlines, tabs and whitespaces at the beginning, the end and if
        there is more than one.
        :param arg: A string, the string which shell be cleaned
        :return: A string, the cleaned string
        """
        # Deletes whitespaces after a newline
        arg = re.sub(re_newline_spc, '', arg)
        # Deletes every whitespace, tabulator, newline at the beginning of the string
        arg = re.sub(re_starting_whitespc, '', arg)
        # Deletes whitespace or tabulator if followed by whitespace or tabulator
        arg = re.sub(re_multi_spc_tab, '', arg)
        #  Deletes newline if it is followed by an other one
        arg = re.sub(re_double_newline, '', arg)
        # Deletes newlines and whitespaces at the end of the string
        arg = re.sub(re_ending_spc_newline, '', arg)
        return arg

    def do_cleaning(self, arg):
        """
        Does the actual cleaning by using the delete methods above.
        :param arg: A string, the string which shell be cleaned. Or a list, in
        which case each of the strings within the list is cleaned.
        :return: A string, the cleaned string. Or a list with cleaned string entries.
        """
        if arg is not None:
            if isinstance(arg, list):
                newlist = []
                if not arg:
                    return None
                for entry in arg:
                    if entry.strip() != '':
                        newlist.append(self.do_cleaning(entry))
                return newlist
            # else:    # Commented as Python version will always be > 3
            # if sys.version_info[0] < 3:
            #     arg = unicode(arg)
            # else:
            arg = str(arg)
            if arg.strip() == '':
                return None
            arg = self.delete_tags(arg)
            arg = self.delete_whitespaces(arg)
            return arg
        # else:
        return None

    def clean(self, list_article_candidates):
        """
        Iterates over each article_candidate and cleans every extracted data.
        :param list_article_candidates: A list, the list of
        ArticleCandidate-Objects which have been extracted
        :return: A list, the list with the cleaned ArticleCandidate-Objects
        """
        # Save cleaned article_candidates in results.
        results = []

        for article_candidate in list_article_candidates:
            article_candidate.title = self.do_cleaning(article_candidate.title)
            article_candidate.description = self.do_cleaning(
                article_candidate.description)
            article_candidate.text = self.do_cleaning(article_candidate.text)
            article_candidate.topimage = self.do_cleaning(
                article_candidate.topimage)
            article_candidate.author = self.do_cleaning(
                article_candidate.author)
            article_candidate.publish_date = self.do_cleaning(
                article_candidate.publish_date)
            article_candidate.category = self.do_cleaning(
                article_candidate.category)
            results.append(article_candidate)

        return results
