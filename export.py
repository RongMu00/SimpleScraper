import json


with open('rawdata.txt', encoding='utf-8') as raw_data_file:


    container_list = json.loads(raw_data_file.readlines())
    #glb_dict_word
    word_freq_dict = container_list[0]
    word_freq_dict = sorted(word_freq_dict, key=lambda x: -x[1])
    word_freq_dict = word_freq_dict[:50]
    #glb_dict_count
    longest_page_dict = container_list[1]
    longest_page_dict = sorted(longest_page_dict, key=lambda x: -x[1])
    longest_word_page = longest_page_dict[0][0]
    #glb_link_list
    unique_page_list = container_list[2]
    num_of_unique_pages = len(unique_page_list)
    #subdomain_dict
    subdomain_list = []
    subdomain_dict = container_list[3]
    subdomain_dict = sorted(subdomain_dict, key=lambda x: x[0])
    for item in subdomain_dict:
        ele = item[0] + ', ' + item[1]
        subdomain_list.append(ele)

with open('report.txt', 'w') as report:
    report.write("50 common words with their frequencies\n")
    for item in word_freq_dict:
        piece = item[0] + " " + str(item[1]) + "\n"
        report.write(piece)

    report.write("\n")
    unique_page_report = "number of unique pages: " + str(num_of_unique_pages) + "\n"
    report.write(unique_page_report)

    report.write("\n")
    longest_page_report = "longest page in terms of words: " + str(longest_word_page) + "\n"
    report.write(longest_page_report)

    report.write("\n")
    subdomain_freq_report = "subdomains and the number of unique pages for each subdomain: " + "\n"
    for rep in subdomain_list:
        report.write(rep)

















