"""
MyFTPClient.py

Allows for connecting to, and downloading and uploading from/to FTP Servers.
MyFTPTool.choose_ftp_func() should be used to make use of class
"""


# imports
import os
import ftplib

from sys import version_info
from socket import gaierror


class MyFTPClient:
    """ Connects to FTP for uploading and downloading."""
    def __init__(self, *args, **kwargs):
        self.hostname = None
        self.username = None
        self.password = None


        self.kwargs = kwargs
        self._unpack_kwargs()

        if self.hostname:
            pass
        else:
            self.hostname = self.getHostName()

        self.FtpCxn = self.connect()

        self.login()

    def _unpack_kwargs(self):
        if "hostname" in self.kwargs:
            self.hostname = self.kwargs['hostname']
        if "username" in self.kwargs:
            self.username = self.kwargs['username']
        if "password" in self.kwargs:
            self.password = self.kwargs['password']

    def connect(self):
        while True:
            try:
                print("Attempting to connect to {}".format(self.hostname))
                self.FtpCxn = ftplib.FTP(host=self.hostname)
                break

            except gaierror as e:
                raise gaierror("Host: {} could not be found. Please try again.".format(self.hostname))
            except WindowsError as e:
                if e.winerror == 10060 or e.winerror == 10061:
                    raise WindowsError("Host: {} could not be found. Please try again.\n".format(self.hostname))
                else:
                    raise e

        print("**** Connection Successful! ****")
        return self.FtpCxn

    # noinspection PyMethodMayBeStatic
    def getHostName(self):
        default_host_name = "10.56.211.116"
        try:
            if version_info.major >= 3:
                hn = input(f"Please Enter Hostname or IP address [{default_host_name}]: ")
            else:
                # noinspection PyUnresolvedReferences
                hn = raw_input("Please Enter Hostname or IP address [{}]: ".format(default_host_name))
        except KeyboardInterrupt:
            print("Ok Quitting!!")
            exit(0)

        if len(hn) > 0:
            return hn
        else:
            print("returning default hostname {}".format(default_host_name))
            return default_host_name

    def login(self):
        while True:
            try:
                print("**** Please Login to {} ****".format(self.hostname))
                if self.username and self.password:
                    pass
                else:
                    try:
                        self.username = input("User: ")
                        self.password = input("Password: ")
                    except KeyboardInterrupt:
                        print("Ok Quitting!")
                        exit(0)

                if self.FtpCxn.login(self.username, self.password):
                    print(self.FtpCxn.getwelcome())
                    print("****** Login Successful! ******")
                    print("****** Welcome {}! ******".format(self.username))
                    break
                else:
                    # stderr.write("Login not successful, please try again.")
                    print("Login not successful, please try again.")
            except ftplib.error_perm as e:
                raise e

    def _get_ftp_dir(self):
        print("\nAvailable files/folders in {} are: ".format(" '{}' ".format(self.FtpCxn.pwd())))
        for item in self.FtpCxn.nlst():
            print(item)

        while True:
            new_ftp_dir = input("Choose a new folder (press q to quit): ")
            if new_ftp_dir in self.FtpCxn.nlst():
                self.FtpCxn.cwd(new_ftp_dir)
                print("Current FTP Server directory is: {}".format(self.FtpCxn.pwd()))
                break

            elif new_ftp_dir.lower() == 'q':
                print("Ok, Quitting...")
                exit(0)

            elif not os.path.isdir(new_ftp_dir):
                print("folder '{}' not found, please try again".format(new_ftp_dir))

    def _ftp_dir_list(self):
        print("\nAvailable files/folders in {} are: ".format(" '{}' ".format(self.FtpCxn.pwd())))
        for item in self.FtpCxn.nlst():
            print(item)

    def _get_save_dir(self):
        while True:
            try:
                choice = input("Please choose location of the file to upload"
                               "\n or the save location for the downloaded file (or type default) (press q to quit): ")
                if choice == 'q':
                    print("Ok, Quitting...")
                    exit(0)

                elif choice == 'default':
                    choice = '../Misc_Project_Files'
                    print("defaulting to {}".format(choice))
                    return choice

                elif os.path.isdir(choice):
                    print("Folder validated")
                    return choice

                elif not os.path.isdir(choice):
                    print("Folder not detected, please try again.")
            except FileNotFoundError as e:
                raise e

    def choose_file(self, transfer_type):
        self._ftp_dir_list()
        while True:
            change_dir_q = input("Would you like to change directories? (y/n or q to quit): ").lower()
            if change_dir_q == 'y':
                self._get_ftp_dir()
                break
            elif change_dir_q == 'n':
                break
            elif change_dir_q == 'q':
                print("Ok, Quitting...")
                exit(0)
            else:
                print("Please choose \'y\', \'n\', or press \'q\' to quit.")
        savedir = self._get_save_dir()
        try:
            os.chdir(savedir)
        except FileNotFoundError as e:
            raise e

        self._ftp_dir_list()
        while True:
            if transfer_type == 'upload':
                filename = input("Please enter the name of the file to upload: ")
                if filename in os.listdir(savedir):
                    print("{} chosen".format(filename))
                    return filename
                else:
                    print("\'{}\' not found in, \'{}\' please try again.".format(filename, savedir))

            elif transfer_type == 'download':
                filename = input("Please enter the name of the file to download: ")
                if filename in self.FtpCxn.nlst():
                    print("{} chosen".format(filename))
                    return filename
                else:
                    print("\'{}\' not found in, \'{}\' please try again.".format(filename, self.FtpCxn.pwd()))

    def attempt_download(self, filename):
        try:
            with open(filename, 'wb') as localfile:
                self.FtpCxn.retrbinary('RETR ' + filename, localfile.write, 1024)
                print('File downloaded successfully!')
        except ftplib.Error as e:
            os.remove(filename)
            raise e

    def upload_file_to_ftp(self, filename):
        try:
            self.FtpCxn.storbinary('STOR ' + filename, open(filename, "rb"))
            print("{} uploaded".format(filename))
            self.choose_ftp_func()
        except ftplib.Error as e:
            print("Error, file could not be uploaded. \nErrormsg: {}".format(e))
            raise e

    def choose_ftp_func(self):
        function_choices = {1: "Upload",
                            2: "Download",
                            3: "Change Directory"}

        for c in function_choices:
            print(str(c) + ". " + function_choices[c])

        # choose function loop
        while True:
            try:
                choice = input("Please Enter the line number of the function "
                               "you would like to run (or press q to quit): ").lower()
            except KeyboardInterrupt:
                print("ok Quitting!!")
                exit(0)

            # noinspection PyUnboundLocalVariable
            if choice == 'q':
                print("Ok, Quitting...")
                exit(0)
            elif int(choice) in function_choices.keys():
                if function_choices[int(choice)].lower() == 'download':

                    file_to_download = self.choose_file(transfer_type='download')
                    self.attempt_download(file_to_download)
                elif function_choices[int(choice)].lower() == "upload":
                    file_to_download = self.choose_file(transfer_type='upload')
                    self.upload_file_to_ftp(file_to_download)
                break
            else:
                print("Please choose a line number from the list above.")

if __name__ == "__main__":
    ftp_tool = MyFTPClient()
    ftp_tool.choose_ftp_func()
