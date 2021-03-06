import pandas as pd
valid_staff = 0
invalid_staff = 0


def indexing(file_name):
    df1 = pd.read_csv(file_name)
    df1 = df1.set_index(['university', 'staffName'])
    df1.to_csv(file_name)


def query(staff):
    """Perform Google Scholar query and return author object"""
    import scholarly
    try:
        search_query = scholarly.search_author(staff.rstrip())
    except ConnectionError:
        print('Connection aborted.When querying ' + staff)
        return None

    try:
        author = next(search_query).fill()
        return author
    except StopIteration:
        print('Generator cannot be iterated! When querying ' + staff.rstrip())
        return None


def staff_query(uni_name):
    """find citation data of staffs and calculate the h-index of them then store it as a dataFrame in a csv file"""
    import GoogleQuery as gq
    import dataProcess as dp
    global valid_staff
    global invalid_staff
    f = open('staffLists\\' + uni_name + '.txt', 'r', encoding='utf-8')
    df = pd.DataFrame()
    for line in f:
        cite = []
        titles = []
        staffs = []
        query_result = query(line)
        if query_result:
            if query_result.name != line.rstrip():
                continue
            if query_result.name not in staffs:
                staffs.append(query_result.name)
                sorted_cite = get_sorted_pub_info(query_result, 2014, 0)
                if sorted_cite:
                    for title, eachcite in sorted_cite.items():
                        titles.append(title)
                        cite.append(eachcite)
                    hindex = dp.get_hindex(cite)
                    try:
                        sub_series = gq.init_series(uni_name, query_result.name, cite, int(hindex))
                        df = df.append([sub_series])
                        print(query_result.name + " saved!")
                        valid_staff += 1
                    except TypeError:
                        print("There is no hindex value for " + query_result.name + "!")
        else:
            invalid_staff += 1
            continue
    with open('uniData\\' + uni_name + '.csv', 'a', encoding='utf-8') as f:
        df = df.drop('Unnamed: 0', 1)
        df.to_csv(f)
        print(uni_name.rstrip() + ' has been saved successfully!')
    indexing('uniData\\' + uni_name + '.csv')


def get_sorted_pub_info(author, ini_year, stop_year):
    """find the citation data of author's publication published in the year limit and sort it in descending order"""
    temp_cite = {}
    sorted_cite = {}
    if ini_year > stop_year & stop_year != 0:
        print("Invalid year range input")
        return None
    else:
        for pub in author.publications:
            if 'year' in pub.bib.keys():
                if stop_year == 0:
                    if pub.bib['year'] > ini_year:
                        if hasattr(pub, 'citedby'):
                            temp_cite[pub.bib['title']] = pub.citedby
                else:
                    if pub.bib['year'] > ini_year & pub.bib['year'] < stop_year:
                        if hasattr(pub, 'citedby'):
                            temp_cite[pub.bib['title']] = pub.citedby
        cite = sorted(temp_cite.items(), key=lambda x: x[1], reverse=True)
        for sortedPub in cite:
            sorted_cite[sortedPub[0]] = sortedPub[1]
        return sorted_cite


def run():
    """run this file"""
    f = open("uniList.txt", 'r', encoding='utf-8-sig')
    for line in f:
        line.encode("ascii", "ignore")
        staff_query(line.rstrip())
    f.close()
    print("Query done!\n" + str(valid_staff) + " of staffs is saved to file.\n" + str(invalid_staff) + " of staffs saved unsuccessfully!")


def single_query(staff_name):
    """perform single scholar query and return its name, citation data and h-index"""
    import dataProcess as dp
    cite = []
    titles = []
    author = query(staff_name)
    sorted_cite = get_sorted_pub_info(author, 2014, 0)
    for title, eachcite in sorted_cite.items():
        titles.append(title)
        cite.append(eachcite)
    hindex = dp.get_hindex(cite)
    print(author.name)
    print("cite: "+ str(cite))
    print("hindex:" + str(hindex))


#  run()