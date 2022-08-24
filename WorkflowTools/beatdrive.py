from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import subprocess

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto-handles authentication.
drive = GoogleDrive(gauth)

# -----------------------------------------------------------------------------------------------------------
"""
Multi purpose script for uploading beats/audio/video files onto Google Drive and converting them into 
Instagram-acceptable audio and video codecs. 

"""

all_beats_id = '17o3bn6lZFk723FeqhZM9Z1IbExp559bN'
subfolder_id_dict = {}
subgenre_id_dict = {}
snippet_folder_id_dict = {} 
bv_folder_id = "1o92-5kaI-uXUiTbuXG6sg5BjeH7RRPsv" # Beat Video Folder

f = drive.ListFile({"q": "mimeType='application/vnd.google-apps.folder' and '" + all_beats_id + "' in parents and trashed=false"}).GetList()
ord_list = list(range(1, len(f) + 1))

for i in range(len(f)):
    subfolder_id_dict[f[i]['title']] = f[i]['id']
    subgenre_id_dict[i+1] = f[i]['id']

for i in range(len(f)): 
    subf = drive.ListFile({"q": "mimeType='application/vnd.google-apps.folder' and '" + subgenre_id_dict[i+1] + "' in parents and trashed=false"}).GetList() 
    snippet_folder_id_dict[i+1] = subf[0]['id']


print("Subfolder ID Dictionary:" + "\n")
print(subfolder_id_dict)
print("Subgenre ID Dictionary:" + "\n")
print(subgenre_id_dict)
print("Snippet Folder ID Dictionary:" + "\n")
print(snippet_folder_id_dict)

# Creates snippet of audio file using FFMPEG 
def createSnippet(mp3file): 
    title = mp3file
    print(f'Creating snippet for {title}...')
    print("\n")
    snippet_title = title[:-4] + "_snippet"
    snippet_title_mp3 = title[:-4] + "_snippet.mp3"    
    os.chdir('C://Users/hansu/Desktop/DOCKET')
    ffmpeg_title = title + ".mp3" 
    subprocess.call(['ffmpeg', '-i', title, '-ss', '00:00:00', '-to', '00:00:40', '-c', 'copy', snippet_title_mp3])
    print("Snippet successfully created!")
    return snippet_title

# Uploads audio (beat snippet) into subgenre-specific folder on Google Drive
def uploadAudio(mp3file):
    # Parse filename structure 
    # if snippet: 
        # upload into subgenre snippet folder 
    # else 
        # upload into corresponding subgenre folder 

    # if not snippet 
    if mp3file[-5].isdigit():
        subg_cat = mp3file[-5]
        print(f'Uploading {mp3file} to Drive folder {subg_cat}...')
        print("\n")
        file_metadata = {"parents": [{"id": subgenre_id_dict[int(mp3file[-5])], "kind": "drive#childList"}]}
        new_file = drive.CreateFile(file_metadata)
        new_file.SetContentFile(mp3file)
        new_file.Upload() 
        print(f'Successfully uploaded beat!')
        print("\n")
        

    # if snippet 
    elif (mp3file[-1] == "t"):
        # ex.) "....88bpm_5_snippet"
        subg_cat = mp3file[-9]
        print(f'Uploading {mp3file} to Drive snippet folder {subg_cat}...')
        print("\n")
        file_metadata = {"parents": [{"id": snippet_folder_id_dict[int(mp3file[-9])], "kind": "drive#childList"}]}
        new_file = drive.CreateFile(file_metadata)
        ffname = mp3file + ".mp3"
        new_file.SetContentFile(ffname)
        new_file.Upload() 
        print(f'Succesfully uploaded beat snippet!')
        print("\n")

    else:
        print("This file is already a snippet. Please enter a valid file.")


# Deletes file from local storage 
def deleteUploadedFile(mp3file):
    # Find both original mp3 file and snippet 
    # Check that both files have been uploaded to drive (os.walk through drive and check that they're there)
    # If both files in drive, os.remove() files 

    os.chdir('C://Users/hansu/Desktop/DOCKET')
    title = mp3file 

    # If deleting audio 
    if title.endswith('.mp3'):
        title_ext = mp3file + ".mp3"
        snip_title = mp3file[:-4] + "_snippet" # FFmpeg naming artifact 
        snip_title_ext = snip_title + ".mp3"

        file_upload_check = drive.ListFile({'q': "title='"+ title + "' or title='"+ title_ext + "'"}).GetList()
        snip_upload_check = drive.ListFile({'q': "title='" + snip_title + "' or title='" + snip_title_ext + "'"}).GetList()
        if ((len(file_upload_check) > 0) and (len(snip_upload_check) > 0)):
            print(f'Removing {title}...')
            os.remove(title) 
            print(f'Removing {snip_title_ext}...')  
            os.remove(snip_title_ext)
            print("Removed!")
        else:
            print("Either the desired file or the corresponding snippet file hasn't properly been uploaded. Please check and try again.")

    # If deleting video 
    elif title.endswith('.mp4'):
        file_upload_check = drive.ListFile({'q': "title='" + title + "' or title='" + title[:-3] + "'"}).GetList()
        if (len(file_upload_check) > 0): 
            print("Video snippet successfully found in Drive. Eligible to delete. \n")
            print(f'Removing video {title}...')
            os.remove(title) 
            print("Removed video!") 

    # If deleting image
    elif title.endswith('.jpg') or title.endswith('.png') or title.endswith('.jpeg'):
        print(f'Deleting image {title}...')
        os.remove(title)
        print("Removed image!")


# Creates snippet video clip (mp4) by combining snippet beat audio (mp3) with any supported image format (jpg, png, jpeg, gif) using FFMPEG
def createSnippetVideo(mp3file, jpgfile): #mp3file: ......_6.mp3
    # if mp3file is not a snippet: 
        # createSnippet(mp3file) 
        # use snippet and jpgfile to make video snippet 
    if mp3file[-5].isdigit():
        beat_snippet = createSnippet(mp3file) 
        bs_title = beat_snippet + ".mp3"
    else:     
        bs_title = mp3file

    bv_title = bs_title[:-4] + "_vid.mp4"
    subprocess.call(['ffmpeg', '-i', jpgfile, '-i', mp3file, '-acodec', 'aac', '-vcodec', 'libx264', bv_title])
    return bv_title #"___.mp4"


# Uploads video (mp4 file) to Google Drive
def uploadVideo(mp4file): 
    print(f'Uploading video with title {mp4file}...')
    file_metadata = {"parents": [{"id": bv_folder_id, "kind": "drive#childList"}]}
    new_file = drive.CreateFile(file_metadata)
    new_file.SetContentFile(mp4file)
    new_file.Upload() 
    print(f'Successfully uploaded beat snippet video!')
    print("\n")
    pass 


def main():
    # For each beat:    
        # create snippet 
        # upload audio
        # upload snippet 
        # If image (extension .jpg) with the same name: 
            # create snippet video 
            # upload snippet video 
            # delete snippet video 
            # delete image  
        # delete snippet
        # delete audio 

    os.chdir('C://Users/hansu/Desktop/DOCKET')
    docket = [x for x in os.listdir() if x.endswith('.mp3')] # Grab all MP3 files in docket
    
    #docket = os.listdir()

    print("\n")
    print("Current docket: " + "\n")
    print(docket)
    for beat in docket:
        beat_snippet = createSnippet(beat)
        uploadAudio(beat)
        uploadAudio(beat_snippet)
        beat_snip_title = beat_snippet + ".mp3"
        bi_title_jpg = beat[:-4] + ".jpg"
        bi_title_png = beat[:-4] + ".png"
        bi_title_jpeg = beat[:-4] + ".jpeg"
        if (bi_title_jpg in os.listdir()):
            bv = createSnippetVideo(beat_snip_title, bi_title_jpg)
            uploadVideo(bv)
            deleteUploadedFile(bi_title_jpg)
            deleteUploadedFile(bv)
        elif (bi_title_png in os.listdir()):
            bv = createSnippetVideo(beat_snip_title, bi_title_png)
            uploadVideo(bv)
            deleteUploadedFile(bi_title_png)
            deleteUploadedFile(bv)
        elif (bi_title_jpeg in os.listdir()):
            bv = createSnippetVideo(beat_snip_title, bi_title_jpeg)
            uploadVideo(bv) 
            deleteUploadedFile(bi_title_jpeg)
            deleteUploadedFile(bv)
        else:
            print("No image file found. Skipping video creation for now...\n")

        deleteUploadedFile(beat)

main() 

