import urllib
import urllib2

url = "http://racktables.duckdns.org/index.php?module=redirect&page=object&tab=rackspace&op=updateObjectAllocation"

object_id = 5
rack_id = 3
unit_id = 17

post_data = {
'object_id': object_id,
'rackmulti[]': rack_id,
'comment': '',
'got_atoms': 'Save',
'atom_{0}_{1}_0'.format(rack_id, unit_id): 'on',
'atom_{0}_{1}_1'.format(rack_id, unit_id): 'on',
'atom_{0}_{1}_2'.format(rack_id, unit_id): 'on',
}

headers = {
    'Authorization': 'Basic YWRtaW46cm9vdA=='
}

post_data = urllib.urlencode(post_data)
request = urllib2.Request(url, post_data, headers)

print urllib2.urlopen(request).read()