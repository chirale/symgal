# -*- coding: utf-8 -*-
from win32file import CreateSymbolicLink
from wand.image import Image
from wand.exceptions import *
from os import walk, path
from hashlib import md5
from base64 import b16encode

import mimetypes

from Tkinter import Tk, Button, Frame, Label, Entry
import tkMessageBox

from tkFileDialog import askdirectory

class GalleryBatch:
    """
    Recurse subdirectories and symlink sane images.
    MS Windows only.
    """
    def __init__(self):
        self.dirs = {'source': '', 'destination': ''}
        
        self.skip_limit_mb = 50
        self.reset_counter(self.skip_limit_mb)

    def reset_counter(self, lm):

        self.skip_limit_mb = lm
        
        self.nice_images = 0
        self.corrupt_errors = 0
        self.other_errors = 0
        self.already_exists = 0
        self.skip = 0
        

    def filecheck(self, filepath, filename):
        """
        Check image file and create symbolic link.
        
        Generated file pattern: DESTINATION/FILENAME_[BASE16].EXT
        Note: the same file into N different subdirectory has N symbolic links.
        """        
        try:
            # get approx size in MB
            # @see http://stackoverflow.com/a/6080504/892951
            filesize = path.getsize(filepath) >> 20
            assert filesize < self.skip_limit_mb
            with Image(filename=filepath) as img:
                assert img.format != "TXT"
                filenamenoext, ext = path.splitext(filename)
                fto = "%s%s_[%s]%s" % (self.dirs['destination'] + path.sep, filenamenoext, b16encode(md5(filepath).digest()), ext)
                try:
                    CreateSymbolicLink(fto, filepath, 0)
                    self.nice_images += 1
                except:
                    self.already_exists += 1
                    pass
        # @see http://dahlia.kr/wand/wand/exceptions.html#wand.exceptions.CorruptImageError
        except (CorruptImageError, CorruptImageWarning, CorruptImageFatalError):
            self.corrupt_errors += 1
        except (MissingDelegateError, AssertionError):
            # skip non image file / big files
            self.skip += 1
            pass
        except:
            # BlobError (cannot read/access) and more
            self.other_errors += 1

    def imgwalk(self):
        # @see http://stackoverflow.com/a/120701/892951
        for dirname, dirnames, filenames in walk(self.dirs['source']):
            for subdirname in dirnames:
                pass
            for filename in filenames:
                filepath = path.join(dirname, filename)
                self.filecheck(filepath, filename)
        return """Succeded: %d.
Corrupted: %d.
Already exists: %d.
Skipped: %d.
Other errors: %d.
Total: %d.""" % (self.nice_images, self.corrupt_errors, self.already_exists, self.skip, self.other_errors, self.nice_images+self.corrupt_errors+self.skip+self.already_exists+self.other_errors)

    def run(self, lm):
        self.reset_counter(lm)

        print self.skip_limit_mb
        
        try:
            msg = "Please choose source and destination directories."
            assert self.dirs['source'] != ""
            assert self.dirs['destination'] != ""

            msg = "Source and destination directories must differ."
            assert self.dirs['source'] != self.dirs['destination']
            
            tkMessageBox.showinfo(
                "Finished",
                self.imgwalk()
            )
            
        except(AssertionError):
            tkMessageBox.showerror(
                "Choose directories",
                msg
            )
        finally:
            pass


# Tk application start here
class Application(Frame):
    def chodir(self, gb, key):
        gb.dirs[key] = askdirectory(initialdir="/", parent=root)
        # normalized version of directory path
        # @see http://docs.python.org/2/library/os.path.html#os.path.normpath
        dirnormpath = path.normpath(gb.dirs[key])
        if key == "source":
            self.srctxt['text'] = dirnormpath
        if key == "destination":
            self.dsttxt['text'] = dirnormpath
    def createWidgets(self):
        gb = GalleryBatch()

        self.src = Button(self)
        self.src["text"] = "Find images (subdirectories included)"
        self.src["command"] = lambda: self.chodir(gb, "source")
        self.src.pack({"fill":"x"})

        self.srctxt = Label(self)
        self.srctxt['text'] = "Select source directory"
        self.srctxt.pack({"fill":"x"})

        self.dst = Button(self)
        self.dst["text"] = "Create symlink gallery to"
        self.dst["command"] = lambda: self.chodir(gb, "destination")
        self.dst.pack({"fill":"x"})

        self.dsttxt = Label(self)
        self.dsttxt['text'] = "Select destination directory"
        self.dsttxt.pack({"fill":"x"})

        self.runop = Button(self)
        self.runop["text"] = "Run"
        self.runop["bg"]   = "#008000"
        self.runop["fg"]   = "white"
        self.runop["command"] = lambda: gb.run(self.skip_mb.get())
        self.runop.pack({"side":"right"})

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit
        self.QUIT.pack({"side":"left"})

        self.skip_mb_label = Label(self, text="Ignore file larger than (MB)")
        self.skip_mb_label.pack()
        self.skip_mb = Entry()
        self.skip_mb.insert(0, gb.skip_limit_mb)
        self.skip_mb.pack()
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
root.title("SymGal")
app = Application(master=root)
app.mainloop()
root.destroy()
