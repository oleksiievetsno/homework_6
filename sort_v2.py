from pathlib import Path
import sys
import shutil
import os

'''This version skips files with unknown extension. And maybe renaming folders'''
# Lists of files for an output
files_audio = []
files_images = []
files_video = []
files_documents = []
files_archives = []
files_unknown = []

# Known and unknown lists
known_ext = set()
unknown_ext = set()

# Folders, which we need for sorting
folders = ('images', 'audio', 'video', 'documents',
           'archives')

# Tuples with used extension.
# We could add later more extensions to corresponding tuples
images_ext = ('.jpeg', '.png', '.jpg', '.svg')
video_ext = ('.avi', '.mp4', '.mov', '.mkv')
docs_ext = ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx')
audio_ext = ('.mp3', '.ogg', '.wav', '.amr')
archives_ext = ('.zip', '.gz', '.tar')


def normalize(filename):
    '''Normalizing the name of the files and folders, returning new name as a string'''

    # Symbols for normalizing the name
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"

    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

    TRANS = {}

    for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = t
        TRANS[ord(c.upper())] = t.upper()

    new_name = ''
    for char in filename:
        new_char = TRANS.get(ord(char))
        if new_char:
            new_name += new_char
        # if char is [a-zA-z0-9]
        elif 97 <= ord(char) <= 122 or 65 <= ord(char) <= 90 or 49 <= ord(char) <= 57:
            new_name += char
        else:
            new_name += '_'

    return new_name  # returning new name as a string


def get_folder():
    """Obtaining folder from arguments in command line"""
    try:
        return sys.argv[1]
    except:
        print("Please enter the path of a folder -- only one argument")


def folder_sorter(path):
    '''This is a main function, which takes the path as an argument and perform sorting inside the given folder'''
    p = Path(path)
    for item in p.iterdir():
        if item.is_dir():
            if item.name in folders:  # skipping the images, video... folders
                continue
            # elif len(os.listdir(item)) == 0 and item.name not in folders: # if folder is empty, let's delete it. The final cleaning is at the end of the script
            #     shutil.rmtree(item)  # If so, delete it
            else:
                # renaiming the current folder with normalized name

                new_name = normalize(item.name)
                new_file = Path(f'{item.parent}/{new_name}')
                os.rename(item, new_file)

                # recursive folder sorting
                folder_sorter(new_file)
        elif item.is_file():
            file_sorter(item)  # then proceed with file sorting


def file_rename(path, new_name, extension):
    '''Function for renaming the files '''
    p = Path(path)
    p.rename(Path(p.parent, new_name + extension))
    new_file = Path(new_name + extension)
    return new_file


def file_sorter(path):
    '''Function for reading the extensions of files, renaming them and putting in the right folder '''

    p = Path(path)
    extension = p.suffix  # getting an extension of a file
    name = p.stem  # name without an extension

    # Translating and normalizing the name
    new_name = normalize(name)

    # Renaming the file if it's known enxtension

    new_file = file_rename(p, new_name, extension)

    # Adding the new name to the list
    # adding extensions to known and unknown lists
    # moving file to corresponding folder
    if extension in images_ext:
        files_images.append(new_name + extension)
        known_ext.add(extension)
        shutil.move(f'{p.parent}/{new_file}',
                    f'{MAIN_FOLDER}/images/{new_file}')
    elif extension in video_ext:
        files_video.append(new_name + extension)
        known_ext.add(extension)
        shutil.move(f'{p.parent}/{new_file}',
                    f'{MAIN_FOLDER}/video/{new_file}')
    elif extension in docs_ext:
        files_documents.append(new_name + extension)
        known_ext.add(extension)
        shutil.move(f'{p.parent}/{new_file}',
                    f'{MAIN_FOLDER}/documents/{new_file}')
    elif extension in audio_ext:
        files_audio.append(new_name + extension)
        known_ext.add(extension)
        shutil.move(f'{p.parent}/{new_file}',
                    f'{MAIN_FOLDER}/audio/{new_file}')
    elif extension in archives_ext:
        files_archives.append(new_name + extension)
        known_ext.add(extension)
        shutil.unpack_archive(f'{p.parent}/{new_file}',
                              f'{MAIN_FOLDER}/archives/{new_file}')
        os.remove(f'{p.parent}/{new_file}')
    else:
        files_unknown.append(name + extension)
        if extension:
            unknown_ext.add(extension)
        # shutil.move(f'{p.parent}/{new_file}',
        #            f'{MAIN_FOLDER}/unknown_extensions/{new_file}')


if __name__ == '__main__':

    p = Path(get_folder())

    MAIN_FOLDER = p  # defining main folder, from which all the recursions start

    if p.is_dir():

        # creating folders for images, video ...
        for folder in folders:
            if not os.path.exists(f'{MAIN_FOLDER}/{folder}'):
                os.makedirs(f'{MAIN_FOLDER}/{folder}')

        # main function runs here
        folder_sorter(p)

        # going once again through the main folder and deleting all empty folders
        for p in Path(p).glob('**/*'):
            if p.is_dir() and len(list(p.iterdir())) == 0 and p.name not in folders:
                os.removedirs(p)
        print(f'Images: {files_images}\nVideo: {files_video}\nAudio: {files_audio}\nDocuments: {files_documents}\nArchives: {files_archives}\n\nKnown extensions: {known_ext}\nUnknown extensions: {unknown_ext}')

    else:
        print("It is not a folder")
