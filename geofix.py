import android, sys, os, sqlite3
from datetime import datetime
#Specify the destination directory for storing geographical data
geofix_dir = '/sdcard/Geofix/'
wait = 9000
#Create the destination directory if it doesn't exist
if not os.path.exists(geofix_dir):
    os.makedirs(geofix_dir)
#Enable location, and obtain location data
droid = android.Android()
droid.startLocating()
droid.eventWaitFor('location', int(wait))
location = droid.readLocation().result
droid.stopLocating()
#Generate date and time stamps
dtstamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
#Extract latitude and longitude coordinates from the network source
try:
    coords = location['network']
    lat = coords['latitude']
    lon = coords['longitude']
    droid.makeToast('Network coordinates: ' + str(lat) + ' ' + str(lon))
    #Reverse geocoding to obtain country and city
    result = droid.geocode(lat, lon).result
    geocode_data = droid.geocode(lat, lon)
    country = geocode_data.result[0]['country_name']
    city = geocode_data.result[0]['locality']
    place = city + ', ' + country
except (KeyError):
    place = '--'
    #If network source is not available, extract latitude and longitude values from GPS
    try:
        coords = location['gps']
        lat = coords['latitude']
        lon = coords['longitude']
        droid.makeToast('GPS coordinates', str(lat) + ' ' + str(lon))
    except (KeyError):
        droid.makeToast('Geofix', 'Failed to obtain coordinates.')
        sys.exit()
#Generate an OpenStreetMap URL and save the prepared data in the geofix.tsv file
osm ='http://www.openstreetmap.org/index.html?mlat=' + str(lat) + '&mlon=' + str(lon) + '&zoom=18'
f_path = geofix_dir + 'geofix.tsv'
f = open(f_path,'a')
f.write(str(dtstamp) + '\t' + str(lat) + '\t' + str(lon) + '\t' + place + '\t' + osm + '\n')
f.close()
#Save the prepared data in the geofix.sqlite database
if os.path.exists(geofix_dir + 'geofix.sqlite'):
    sql_query = "INSERT INTO geofix (dtstamp, lat, lon, place, osm_url) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (dtstamp, lat, lon, place, osm)
    conn = sqlite3.connect(geofix_dir + 'geofix.sqlite')
    conn.execute(sql_query)
    conn.commit()
    conn.close()
else:
    #Create the database if it doesn't exist
    conn = sqlite3.connect(geofix_dir + 'geofix.sqlite')
    conn.execute("CREATE TABLE geofix (id INTEGER PRIMARY KEY, dtstamp VARCHAR, lat VARCHAR, lon VARCHAR, place VARCHAR, osm_url VARCHAR)")
    sql_query = "INSERT INTO geofix (dtstamp, lat, lon, place, osm_url) VALUES ('%s', '%s', '%s', '%s', '%s')" % (dtstamp, lat, lon, place, osm)
    conn = sqlite3.connect(geofix_dir + 'geofix.sqlite')
    conn.execute(sql_query)
    conn.commit()
    conn.close()

droid.vibrate()

#Uncomment the code below to show the obtained GPS coordinates on the map
# droid.dialogCreateAlert("OpenStreetMap","Show location on the map?")
# droid.dialogSetPositiveButtonText("Yes")
# droid.dialogSetNegativeButtonText("No")
# droid.dialogShow()
# response=droid.dialogGetResponse().result
# droid.dialogDismiss()
# if response.has_key("which"):
#     result=response["which"]
#     if result=="positive":
#         droid.startActivity('android.intent.action.VIEW', osm)
