from scholarly import scholarly

# Retrieve the author's data, fill-in, and print
# search_query = scholarly.search_author('Steven A Cholewiak')
search_query = scholarly.search_author('moquillaza, unmsm')
author = next(search_query).fill()
print(author)