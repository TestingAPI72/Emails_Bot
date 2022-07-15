from Run_File import run_file
from list_of_files import list_of_files


class Executor:

    def start_process(self):
        """Create Object for run_file and List_of_files class"""
        obj1 = run_file()
        obj2 = list_of_files()
        """Call method of each class in sequence way, or it will collide"""
        obj2.disk_cleanup()
        obj2.download_files_from_gmail()
        obj1.pre_cleanup_txt()
        obj1.resume_exists()
        obj1.check_files_present()
        obj1.change_docx_to_text()
        obj1.generator_email()
        obj1.get_emails()
        obj1.sending_emails()


