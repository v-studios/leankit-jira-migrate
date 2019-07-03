#!/usr/bin/env python
# The 'leankit' library on PyPi doesn't have a way to access tasks, so not useful;
# but does allow access to card.comments:
# [{'Editable': True,
#   'Id': 864199509,
#   'PostDate': '07/03/2019 at 09:00:59 AM',
#   'PostedByFullName': 'Chris Shenton',
#   'PostedByGravatarLink': '92418b85bf0a217061685b44cb1bbf3a',
#   'PostedById': 55921342,
#   'TaggedUsers': None,
#   'Text': '<p>I am a comment</p>'}]
# In LeanKit, accessing a Task shows the same shape URL as for card, e.g.,
# - Card showing tasks: https://v-studios.leankit.com/card/863683312/tasks
# - A task by itself:   https://v-studios.leankit.com/card/863688796

import csv
import os

from jira.client import JIRA
import requests
import requests.auth

BOARD_SUBTASKS = 863679045
BOARD = BOARD_SUBTASKS
CARD_SUBTASKS = 863683312
DOMAIN = os.environ['LEANKIT_DOMAIN']  # bare domain, excluding ".leankit.com"
USER = os.environ['LEANKIT_EMAIL']  # user@company.com
PASSWD = os.environ['LEANKIT_PASSWD']
API = f'https://{DOMAIN}.leankit.com/io'

# JIRA_URL = 'https://v-studios.atlassian.net'
# JIRA_API = f'{JIRA_URL}/rest/api/2/'
# JIRA_USER = os.environ['JIRA_USER']
# JIRA_TOKEN = os.environ['JIRA_TOKEN']  # Gotten from Atlassian

# # This works:
# res = requests.get(f'{JIRA_API}/search?jql=project=SPEC&maxResults=2',
#                    auth=(JIRA_USER, JIRA_TOKEN))
# pp(res)

# Can't get this to work:
#jac = JIRA(JIRA_URL, basic_auth=(JIRA_USER, JIRA_PASS))
#jac = JIRA(JIRA_URL, auth=(JIRA_USER, JIRA_TOKEN))
# exit(0)


auth = requests.auth.HTTPBasicAuth(USER, PASSWD)
boards = requests.get(f'{API}/board', auth=auth).json()

# Board metadata
# board_subtasks = requests.get(f'{API}/board/{BOARD_SUBTASKS}', auth=auth).json()

# List of cards on board
# TODO we have to page through this with limit=20 (default) and offset
# 'pageMeta': {'endRow': 5, 'limit': 20, 'offset': 0, 'startRow': 1, 'totalRecords': 5}}

# If I walk ALL cards does it list the Tasks, note the Subtask attr:
# 'cardType': {'id': '863679053', 'name': 'Subtask'},

res = requests.get(f'{API}/card?board={BOARD_SUBTASKS}', auth=auth).json()

# Getting comments:
# A Task has comments right in the item
# but for a Card we have to ask, how stupid

csvfile = open(f'board-{BOARD}-comments.csv', 'w')  # newline=''?
csvout = csv.DictWriter(csvfile, fieldnames=('card_id', 'title', 'comment'), dialect='excel', quoting=csv.QUOTE_ALL)
csvout.writeheader()

for card in res['cards']:
    cid = card['id']
    title = card['title']       # required for import, even comments??
    res = requests.get(f'{API}/card/{cid}/comment', auth=auth).json()
    for comment in res['comments']:
        email = comment['createdBy']['emailAddress']
        text = comment['text']
        dt = comment['createdOn']
        print(f'card id={cid} dt={dt} email={email} text={text}')
        csvout.writerow({'card_id': cid, 'title': title, 'comment': text})

    # if 'comments' in card:
    #     print(f'card id={card["id"]} comments={card["comments"]}')  # multiples, with dates and people
    # else:
    #     #print(f'NOCOMMENT {card}')
    #     import pdb; pdb.set_trace()

        

exit(0)


# Getting Cards' Tasks:
for card in res['cards']:
    #print(f'card={card}')
    cid = card['id']
    tbs = card['taskBoardStats']
    # None or: 'taskBoardStats': {'totalCount': 3, 'completedCount': 1, 'totalSize': 3, 'completedSize': 1}}
    print(f'card id={cid} title={card["title"]} taskBoardStats={tbs} cardType={card.get("cardType", "NONE")}')
    if tbs:
        res = requests.get(f'{API}/card/{cid}/tasks', auth=auth).json()
        # TODO we'll actually have to page through tasks too, default limit 200
        for ctask in res['cards']:    # interesting: cards, not taskstasks
            tid = ctask['id']
            print(f'task cid={ctask["containingCardId"]} tid={tid} ttitle={ctask["title"]}')
            # It doesn't give us description so we have to go fish again
            task = requests.get(f'{API}/card/{cid}/tasks/{tid}', auth=auth).json()  # doesn't return parent card id
            #
            print(f'TASK details id={task["id"]} tags={task["tags"]} size={task["size"]} priority={task["priority"]}'
                  f' lane={task["lane"]["title"]} email={task["createdBy"]["emailAddress"]}'
                  f' title={task["title"]} description={task["description"]}')

