import urllib.request
from urllib.request import urlopen
from urllib.request import Request
import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from lxml import html
import copy
from collections import defaultdict
import json
from lxml import etree

stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as',
              'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot',
              'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few',
              'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll",
              "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll",
              "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most',
              "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our',
              'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should',
              "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves',
              'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those',
              'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're",
              "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while',
              'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll",
              "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

# robots = ['https://www.informatics.uci.edu/robots.txt', 'https://www.ics.uci.edu/robots.txt', 'https://www.cs.uci.edu/robots.txt',
#           'https://www.stat.uci.edu/robots.txt']


urldict = dict()


glb_dict_word = {} # key is word, value is frequence
glb_dict_count = {} # key is url, value is word count.
glb_link_list = []  #
subdomaindict = defaultdict(int)

def scraper(url, resp):
    global glb_dict_word, glb_dict_count
    scraper_lst = []
    links = extract_next_links(url, resp)
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    if links == []:
        return list()
    bt_soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    tokenized_lst = tokenizer.tokenize(bt_soup.get_text())
    count_lst = 0
    for w in tokenized_lst:
        w = w.casefold()
        if w not in stop_words:
            count_lst += 1
            # global glb_dict_word
            if w in glb_dict_word:
                glb_dict_word[w] += 1
            else:
                glb_dict_word[w] = 1
    glb_dict_count[resp.url] = count_lst
    for link in links:
        #filtered_lst = []
        #count_lst = 0
        if is_valid(link):
            scraper_lst.append(link)
            #bt_soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            #tokenized_lst = tokenizer.tokenize(bt_soup.get_text())

            # for w in tokenized_lst:
            #     w = w.casefold()
            #     if w not in stop_words:
            #         count_lst += 1
            #         # global glb_dict_word
            #         if w in glb_dict_word:
            #             glb_dict_word[w] += 1
            #         else:
            #             glb_dict_word[w] = 1
            # global glb_dict_count
            #glb_dict_count[resp.url] = count_lst
                    #filtered_lst.append(w)
    global glb_link_list
    glb_link_list = scraper_lst
    with open('rawdata.txt', 'w') as raw_data_file:
        raw_data_file.writelines(json.dumps(glb_dict_word))
        raw_data_file.writelines(json.dumps(glb_dict_count))
        raw_data_file.writelines(json.dumps(glb_link_list))
        raw_data_file.writelines(json.dumps(subdomaindict))

    return scraper_lst
    #return [link for link in links if is_valid(link)]
# def scraper(url, resp):
#     links = extract_next_links(url, resp)
#     if links == []:
#         return list()
#     with open('rawdata.txt', 'w') as raw_data_file:
#         raw_data_file.writelines(json.dumps(glb_dict_word))
#         raw_data_file.writelines(json.dumps(glb_dict_count))
#     return [link for link in links] #if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    url_list = list()
    urldiff = set()

    if resp.raw_response is None:
        return list()
    if resp.status == 204:
        return list()

    if resp.status >= 200 and resp.status <= 299:
        html_content = resp.raw_response.content
        try:
            parsed_str = html.fromstring(html_content)
        except etree.ParserError as err:
            if str(err) == "Document is empty":
                return list()
            raise
        copied_str = copy.deepcopy(parsed_str)
        copied_str.make_links_absolute(resp.url)
        link_parsed = list(parsed_str.iterlinks())
        link_copied = list(copied_str.iterlinks())
        for i in range(len(link_parsed)):
            if is_valid(link_parsed[i][2]):
                if link_copied[i][2] not in urldiff:
                    urldiff.add(link_copied[i][2])
                    no_frag_url = urldefrag(link_parsed[i][2])[0]
                    #link_parsed[i][2] = urldefrag(link_parsed[i][2])[0]
                    url_list.append(no_frag_url)#link_parsed[i][2])
                    parsed = urlparse(no_frag_url)#link_parsed[i][2])
                    if "ics.uci.edu" in parsed.netloc:
                        target = parsed.scheme + "://" + parsed.netloc
                        if target in subdomaindict.keys():
                            subdomaindict[target] += 1
                        else:
                            subdomaindict[target] = 1
        url_list = set(url_list)
        # for i in range(len(link_parsed)):
        #     urldict[link_copied[i]] = link_parsed[i]
        #
        # unique_url = urldict.values()

        # soup = BeautifulSoup(html_content, 'html.parser')
        #
        # for x in soup.find_all('a'):
        #     link = x.get('href')
        #     # if '#' in link:
        #     #     link = link.split('#')[0]
        #     links.add(link)

    else:
        return list()
        # If the response was successful, no Exception will be raised
    return list(url_list)

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        # if not re.match(r"^(\w*.)(ics.uci.edu\\*|cs.uci.edu\\*|informatics.uci.edu\\*|stat.uci.edu\\*|today.uci.edu\\department\\information_computer_sciences\\*)", parsed.path.lower()):
        #     return False

        #replace = parsed._replace(query="", params="", fragment="")

        # netloc_and_path = [parsed.netloc, parsed.path]
        # nap = urlunparse(netloc_and_path)
        #parsed = parsed._replace(fragment="")
        if parsed.netloc == 'today.uci.edu':
            if not re.match(r'\/department\/information_computer_sciences\/.*', parsed.path):
                return False
        if not re.match(r'.*\.(ics|cs|stat|informatics)\.uci\.edu', parsed.netloc): #or not re.match(r'http(s?)\:\/\/today\.uci\.edu\/department\/information_computer_sciences\/', urlunparse(replace)):
            return False
        if parsed.query is not "":
            return False

        #status_code = urllib.request.urlopen(url).getcode()
        # if status_code >= 300 and status_code < 400:
        #     return False
        if 'redirect' in url:
            return False
        if '?replytocom' in url:
            return False
        if 'event' in parsed.query:
            return False
        if 'events' in parsed.path:
            return False
        if 'ical' in parsed.query:
            return False
        if "share" in parsed.query:
            return False
        if "filter" in parsed.query:
            return False

        path_split = url.split('/')
        for x in path_split:
            if re.match(r"#.*", x) != None:
                return False

        counters = Counter(path_split)
        if counters.most_common(1)[0][1] > 2:
            return False

        # if re.match(r".*\.(css|js|bmp|gif|jpe?g|ico"
        #     + r"|png|tiff?|mid|mp2|mp3|mp4"
        #     + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        #     + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
        #     + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        #     + r"|epub|dll|cnf|tgz|sha1"
        #     + r"|thmx|mso|arff|rtf|jar|csv"
        #     + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower()):
        #     return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


# def parse_robots_file(roboturl):
#     invalid = []
#     lines = urlopen(roboturl).read()
#     lines = lines.decode("utf-8").split('\n')
#     for line in lines:
#         if 'Disallow' in line:
#             split = line.split(':', maxsplit=1)
#             url = roboturl.strip('/robots.txt')
#             link = split[1].strip()
#             url = url + link
#             invalid.append(url)
#
#     return invalid
#
#
# def get_sitemap(roboturl):
#     data = []
#
#     lines = urlopen(roboturl).read()
#     lines = lines.decode("utf-8").split('\n')
#     for line in lines:
#         if 'Sitemap' in line:
#             split = line.split(':', maxsplit=1)
#             data.append(split[1].strip())
#
#     return data
