#!/bin/bash
# Send a Fleet letter via AgentMail with body verification
# Usage: bash {baseDir}/scripts/send-letter.sh <recipient> <subject> <letter-file> [cc] [--thread <thread_id>] [--dry-run]
# Example: bash {baseDir}/scripts/send-letter.sh agentslo@agentmail.to "Re: Blind sort" /workspace/memory/letters/my-letter.md shane.slosar@gmail.com --thread abc-123
#
# The letter file may be:
#   - YAML frontmatter (starts with ---): metadata parsed, thread_id auto-detected, body after closing ---
#   - A plain body or archived letter (no leading ---): first standalone --- is the separator, body after it
#   - A plain body (no --- at all): the whole file is the body
#
# Thread continuation:
#   - If --thread <thread_id> is passed, replies to the last message in that thread
#   - If the letter file has YAML frontmatter with thread_id, uses that automatically
#   - --thread overrides frontmatter thread_id
#   - If neither is provided, sends a new message (creates a new thread)
#
# --dry-run: prints the endpoint, mode, and payload preview without sending or making API calls.

# Parse flags
DRY_RUN=0
THREAD_ID_ARG=""
POSITIONAL=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --thread)
      THREAD_ID_ARG="$2"
      shift 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

RECIPIENT="${POSITIONAL[0]}"
SUBJECT="${POSITIONAL[1]}"
LETTER_FILE="${POSITIONAL[2]}"
CC="${POSITIONAL[3]}"

if [ -z "$RECIPIENT" ] || [ -z "$SUBJECT" ] || [ -z "$LETTER_FILE" ]; then
  echo "Usage: send-letter.sh <recipient> <subject> <letter-file> [cc] [--thread <thread_id>] [--dry-run]"
  echo "Example: send-letter.sh agentslo@agentmail.to \"Re: Blind sort\" /workspace/memory/letters/my-letter.md shane.slosar@gmail.com --thread abc-123"
  exit 1
fi

if [ ! -f "$LETTER_FILE" ]; then
  echo "ERROR: Letter file not found: $LETTER_FILE"
  exit 1
fi

API_KEY=$(assistant credentials reveal --service agentmail --field api_key)

export LETTER_FILE THREAD_ID_ARG API_KEY RECIPIENT SUBJECT CC DRY_RUN

# Extract body and send — all in python so JSON encoding is correct
# Values arrive via environment: shell interpolation into python literals
# breaks on apostrophes/quotes (live bug, Aug 12) and is an injection class.
python3 -c "
import json, os, sys, urllib.request, urllib.parse

LETTER_FILE = os.environ['LETTER_FILE']

with open(LETTER_FILE) as f:
    content = f.read()

lines = content.split('\n')

# Detect YAML frontmatter (file starts with standalone ---)
metadata = {}
if lines and lines[0].strip() == '---':
    # Find closing ---
    second_sep = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            second_sep = i
            break
    if second_sep >= 0:
        # Parse metadata between the two --- lines
        for line in lines[1:second_sep]:
            if ':' in line:
                key, _, value = line.partition(':')
                metadata[key.strip()] = value.strip()
        body = '\n'.join(lines[second_sep + 1:]).strip()
    else:
        # Malformed: starts with --- but no closing ---, treat whole file as body
        body = content.strip()
else:
    # No frontmatter — find first standalone --- as separator (backward compat)
    first_separator = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            first_separator = i
            break
    if first_separator >= 0:
        body = '\n'.join(lines[first_separator + 1:]).strip()
    else:
        body = content.strip()

# GATE: refuse to send an empty body
if not body:
    print('ERROR: extracted body is empty. Aborting send.')
    print('Check the file structure — the body should be after the last standalone --- line.')
    sys.exit(1)

# Determine thread_id: CLI arg overrides frontmatter metadata
THREAD_ID = os.environ.get('THREAD_ID_ARG', '') or metadata.get('thread_id', '')

INBOX = 'jrslo-fleet@agentmail.to'
API_KEY = os.environ['API_KEY']
DRY_RUN = int(os.environ.get('DRY_RUN', '0'))

# comma-separated input -> single string or list of strings (API accepts both)
def addr_list(s):
    parts = [p.strip() for p in s.split(',') if p.strip()]
    return parts if len(parts) > 1 else (parts[0] if parts else '')

RECIPIENT = addr_list(os.environ.get('RECIPIENT', ''))
SUBJECT = os.environ.get('SUBJECT', '')
CC = addr_list(os.environ.get('CC', ''))

# GATE: refuse to send with no recipients
if not RECIPIENT:
    print('ERROR: no recipients. Aborting send.')
    sys.exit(1)

# Show what we're about to send so it's verifiable
print(f'Body: {len(body)} chars')
print(f'Preview: {body[:80]!r}...')
print(f'To: {RECIPIENT}')
print(f'CC: {CC or \"none\"}')
print(f'Subject: {SUBJECT}')

if THREAD_ID:
    # REPLY mode: continue an existing thread
    print(f'Mode: REPLY (continuing thread {THREAD_ID})')
    if DRY_RUN:
        print(f'Would fetch thread, find last message_id, and POST to .../messages/{{message_id}}/reply')
        print('---')
        print('DRY RUN — not sending.')
        sys.exit(0)

    # Fetch the thread to get the last message_id
    thread_url = f'https://api.agentmail.to/v0/inboxes/{INBOX}/threads/{THREAD_ID}'
    thread_req = urllib.request.Request(
        thread_url,
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    try:
        thread_resp = urllib.request.urlopen(thread_req)
        thread_data = json.loads(thread_resp.read())
    except urllib.error.HTTPError as e:
        print(f'ERROR fetching thread: HTTP {e.code}: {e.read().decode()[:300]}')
        sys.exit(1)

    messages = thread_data.get('messages', [])
    if not messages:
        print('ERROR: thread has no messages to reply to.')
        sys.exit(1)

    last_msg_id = messages[-1]['message_id']
    # URL-encode the message_id (SMTP IDs contain angle brackets)
    encoded_msg_id = urllib.parse.quote(last_msg_id, safe='')
    endpoint = f'https://api.agentmail.to/v0/inboxes/{INBOX}/messages/{encoded_msg_id}/reply'

    payload_dict = {'to': RECIPIENT, 'text': body}
    if CC:
        payload_dict['cc'] = CC
    # Reply endpoint inherits subject from original message

    print(f'Replying to message: {last_msg_id}')
    print(f'Endpoint: {endpoint}')
    print('---')
else:
    # SEND mode: new thread
    print('Mode: SEND (new thread)')
    endpoint = f'https://api.agentmail.to/v0/inboxes/{INBOX}/messages/send'
    payload_dict = {'to': RECIPIENT, 'subject': SUBJECT, 'text': body}
    if CC:
        payload_dict['cc'] = CC

    print(f'Endpoint: {endpoint}')
    print(f'Payload (sans body): {json.dumps({k: v for k, v in payload_dict.items() if k != \"text\"})}')
    print('---')

    if DRY_RUN:
        print('DRY RUN — not sending.')
        sys.exit(0)

# Send the message
payload = json.dumps(payload_dict).encode()
req = urllib.request.Request(
    endpoint,
    data=payload,
    headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f'message_id: {result.get(\"message_id\", \"?\")}')
    print(f'thread_id: {result.get(\"thread_id\", \"?\")}')
except urllib.error.HTTPError as e:
    print(f'HTTP ERROR {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)
"
