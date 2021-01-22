from xhtml2pdf import pisa
from googleapiclient.discovery import build
from  modules.Credentials import check_credentials


class GDrive():

    def __init__(self, folder_id):
        self.service = build('drive', 'v3', credentials=check_credentials())
        self.files = self.service.files()
        self.folder_id = folder_id


    def file_create(self, file_type, title):
        folder_id = self.folder_id
        file_metadata = {
            "mimeType": file_type,
            "parents": [folder_id],
            "name": title
        }
        file = self.files.create(body=file_metadata, fields='id').execute()
        return file.get('id')


    def files_in_folder(self, size=100):
        folder_id = self.folder_id
        results = self.files.list(q="parents='{0}'".format(folder_id),pageSize=size, fields="files(id,name)").execute()
        return results.get('files', [])


    def list_files(self):
        """
        Return a list with metadata of all files in folder. 
        """
        folder_id = self.folder_id
        return self.files_in_folder()

    
    def get_files_names(self):
        """
        Return a list with the names of all files in folder.
        """
        files_all = self.list_files()
        files_names = []
        
        for elem in files_all:
            files_names.append(elem['name'])
            
        return files_names

    
    def get_files_ids(self):
        """
        Return a list with the ids of all files in folder.
        """
        files_all = self.list_files()
        files_ids = []
        
        for elem in files_all:
            files_ids.append(elem['id'])
            
        return files_ids

    
    def get_file_id(self, file_name):
        """
        Get file id given its name.
        
        :param file_name: file name
        :return: file id
        """
        files_all = self.list_files() 
        
        file_id = None
        for elem in files_all:
            if elem['name'] == file_name:
                file_id = elem['id']
                
        if file_id == None:
            print("There is no file with that name in the folder.")
        
        return file_id

    
    def get_file_name(self, file_id):
        """
        Get file name given its id.
        
        :param file_id: file id
        :return: file name
        """
        files_all = self.list_files() 
        
        file_name = None
        for elem in files_all:
            if elem['id'] == file_id:
                file_name = elem['name']
                
        if file_id == None:
            print("There is no file with that id in the folder.")
        
        return file_name

    
    def delete_file_by_id(self, file_id):
        """
        Delete file given its id.
        
        :param file_id: file id
        """        
        self.file_delete(file_id)    
    
    
    def delete_file_by_name(self, file_name):
        """
        Delete file given its name.
        Note that there may be more than one file with that name in the folder, 
        in which case it will delete the first one it finds.
        
        :param file_name: file name
        """
        file_id = self.get_file_id(file_name)
        self.file_delete(file_id)


    def create_google_sheet(self, file_name):
        """
        Create new empty google sheet in folder and returns its id.
        
        :param file_name: google sheet file name
        """
        return self.file_create(file_type='application/vnd.google-apps.spreadsheet', title=file_name)


    def create_google_slides(self, file_name):
        """
        Create new empty google slides in folder and returns its id.
        
        :param file_name: google slide file name
        """
        return self.file_create(file_type='application/vnd.google-apps.presentation', title=file_name)


    def pdf_export(self, local_file):
        """
        Export local pdf file to google drive folder.
        
        :param local_file: local file name
        """
        folder_id = self.folder_id
        self.file_upload(local_file, mime_type='application/pdf', folder_id=folder_id)


    def png_export(self, local_file): 
        """
        Export local png file to google drive folder.
        
        :param local_file: local file name
        """
        folder_id = self.folder_id
        self.file_upload(local_file, mime_type='image/png', folder_id=folder_id)        

        
    def html_export(self, local_file):
        """
        Export local html file to google drive folder.
        
        :param local_file: local file name
        """
        folder_id = self.folder_id
        self.file_upload(local_file, mime_type='text/html', folder_id=folder_id)

        
    def pptx_export(self, local_file):
        """
        Export local pptx file to google drive folder.
        
        :param local_file: local file name
        """        
        folder_id = self.folder_id
        self.file_upload(local_file, mime_type='application/vnd.oasis.opendocument.presentation', folder_id=folder_id)
        

    def md_export(self, local_file):
        """
        Export local md file to google drive folder.
        
        :param local_file: local file name
        """
        folder_id = self.folder_id
        self.file_upload(local_file, mime_type='text/plain', folder_id=folder_id) 

