import dpkt
import socket
import pygeoip
import time
import requests

gi = pygeoip.GeoIP('GeoLiteCity.dat')

def getPublicIP():
    try:
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            ipData = response.json()
            publicIP = ipData.get('origin')
            return publicIP
        else:
            print("Failed to determine public IP address (Error:{response.status_code})")
    except Exception as e:
        print("Error: {e}")
            

def retKML(dstip, srcip):
    dst = gi.record_by_name(dstip)
    src = gi.record_by_name(srcip)
    try:
        dstlongitude = dst['longitude']
        dstlatitude = dst['latitude']
        srclongitude = src['longitude']
        srclatitude = src['latitude']
        kml = (
            '<Placemark>\n'
            '<name>%s</name>\n'
            '<styleUrl>#transBluePoly</styleUrl>\n'
            '<extrude>1</extrude>\n'
            '<tessellate>1</tessellate>\n'
            '<LineString>'
            '<coordinates>%6f,%6f,0 %6f,%6f,0</coordinates>'
            '</LineString>\n'
            '</Placemark>\n'
        )%(dstip, dstlongitude, dstlatitude, srclongitude, srclatitude)
        return kml
    except:
        return ''
        
def plotIPs(pcap):
    kmlPts = ''
    src = getPublicIP()
    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            dst = socket.inet_ntoa(ip.dst)
            KML = retKML(dst, src)
            kmlPts = kmlPts + KML
        except:
            pass
    return kmlPts

def main():
    f = open('capture.pcap', 'rb')
    pcap = dpkt.pcap.Reader(f)
    kmlHeader = '<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'\
                '<Style id ="transBluePoly">' \
                '<LineStyle>' \
                '<width>1.5</width>' \
                '<color>ffff0000</color>' \
                '</LineStyle>' \
                '</Style>'
    kmlFooter = '</Document>\n</kml>\n'
    kmlDoc = kmlHeader + plotIPs(pcap) + kmlFooter
    r = open('results.kml', 'w')
    r.write(kmlDoc)
    r.close()
    f.close()
    print("Completed successfully.")

if __name__ == "__main__":
    main()
