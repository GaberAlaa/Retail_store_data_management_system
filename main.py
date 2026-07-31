from Modules import finisher , config

def process_all_incoming_files():
    for file_path in sorted(config.INCOMING_FOLDER.glob("*.csv")) :
         finisher.process_file(file_path)

 
 
if __name__ == "__main__":
    process_all_incoming_files()
