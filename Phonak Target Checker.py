#############################################################
#                                                           #
#                   Copyright Bluebotlabz                   #
#                                                           #
#############################################################
import requests
import libhearingdownloader
import xml.etree.ElementTree as xml


print("==================================================")
print("=          Phonak Target Update Checker          =")
print("="*(47-len(libhearingdownloader.downloaderVersion)) + " " + libhearingdownloader.downloaderVersion + " =")

libhearingdownloader.printWaranty()
disclaimer = [
    "DISCLAIMER",
    "",
    "The contributors of the Hearing Aids Fitting Software Update Checkers (\"The Checker\")",
    "do not take any responsability for what you do with The Checker.",
    "",
    "Phonak is a trademark of Sonova AG",
    "Sonova is a trademark of Sonova AG",
    "Phonak is a subsidiary of Sonova AG",
    "Phonak Target is created by Phonak",
    "All rights and credit go to their rightful owners. No copyright infringement intended.",
    "",
    "The contributors of The Checker, and The Checker itself are not affiliated with or endorsed by",
    "Phonak or Sonova AG",
    "Depending on how The Checker is used, it may violate the EULA and/or Terms and Conditions of the associated software(s).",
    "The Checker is an UNOFFICIAL project and the use of associated software(s) may be limited."
]

# Display disclaimer
libhearingdownloader.printDisclaimer(disclaimer)
print("\n\n")



print("Fetching Data...")
xmlns = "{http://cocoon.phonak.com}" # Define the xmlns

updaterRetries = libhearingdownloader.updaterRetries
while updaterRetries > 0:
    try:
        xmlData = requests.get("https://p-svc1.phonakpro.com/1/ObjectLocationService.svc/FittingApplicationInstaller/index?appName=Phonak%20Target&appVer=6.0.1.695&dist=Phonak&country=US&subKeys=").text # Request the updater API (spoof older version to get whole installer files rather than "patch" installers)
        data = xml.fromstring(xmlData)
        break
    except:
        pass

    updaterRetries -= 1
if (updaterRetries == 0):
    print("Error: Update server could not be reached")
    exit(1)

# Previous: Get latest version number (Gets full version from xml and removes the fourth version number as that is not used in files)
# latestVersion = '.'.join((data[0].find(xmlns + "UpdateVersion").find(xmlns + "Version").text).split(".")[:-1])
# Start from v10.0.0, version number from XML doesn't include fourth number anymore.
latestVersion = data[0].find(xmlns + "UpdateVersion").find(xmlns + "Version").text
print("\n\nThe latest available Phonak Target version is v" + latestVersion + "\n\n")

# List of versions
validVersions = [
    (latestVersion, 'The latest available Phonak Target verion'),
#    ('6.2.8', 'The last version of Phonak Target compatible with the iCube (obsolete proprietary hearing aid programmer)'),
    ('manual', 'Manually specify a version (WARNING: ADVANCED USERS ONLY)')
]

# Select outputDir and targetVersion
outputDir = libhearingdownloader.selectOutputFolder()
targetVersion = validVersions[libhearingdownloader.selectFromList(validVersions)][0]
print("\n\n")


# Logic for "special" versions
if (targetVersion == 'latest'):
    targetVersion = latestVersion
elif (targetVersion == 'manual'):
    targetVersion = ''
    while not targetVersion:
        targetVersion = input("Please enter manual target version: ")
        if (len(targetVersion.split('.')) > 3 or not targetVersion.replace('.', '').isdecimal()):
            print("The version you have selected is invalid.\nPlease try again. (hint: it should be in a similar format to a.b.c where a, b, and c are integers)")
        elif (input("You have selected version (" + targetVersion + ") are you sure you want to download it? [Y/n] ") == "n"):
            targetVersion = ''

# Create download folder
outputDir += "Phonak Target " + targetVersion + "/"

# Get CDN/Download location
phonakCDNPath = data[0].find(xmlns + "Location").text

# Get list of files to download for a specified version from the XML data
print ("Downloading directory index")
filesToDownload = {}
for child in data[0].find(xmlns + "ContentInfos"):
    # Construct paths
    filesToDownload[(outputDir + child.find(xmlns + "Key").text).replace(latestVersion, targetVersion)] = (libhearingdownloader.normalizePath(phonakCDNPath, False) + libhearingdownloader.normalizePath(child.find(xmlns + "RemotePath").text, False) + child.find(xmlns + "Key").text).replace(latestVersion, targetVersion)

# Download and save the files
print("Downloading " + str(len(filesToDownload.keys())) + " files\n")
currentFile = 1
for fileToDownload in filesToDownload.keys():
    if (libhearingdownloader.verboseDebug):
        print(filesToDownload[fileToDownload])

    # Download file
    libhearingdownloader.downloadFile(filesToDownload[fileToDownload], fileToDownload, "Downloading " + fileToDownload.split("/")[-1] + " (" + str(currentFile) + "/" + str(len(filesToDownload.keys())) + ")")

    currentFile += 1

print("\n\nDownload Complete!")
