# AnnoBoard README  

## Overview  
AnnoBoard is a tool designed for annotating video datasets based on specific dimensions. This README provides instructions for using the `app.py` script to manage and annotate datasets.  

## File Structure  
- **Video Storage Path**: `./data4dimensions/Prompts4dimensions/{}.txt`  
- **Annotation Storage Path**: `./data4dimensions/anno_files/`  
-****
## Usage  

1. **Setup**  
     Ensure the required directories and files are in place:  
     - Video prompts should be stored in the `Prompts4dimensions` directory.  
     - Annotation files should be stored in the `anno_files` directory.  

2. **Run the Script**  
     Execute the `app.py` script to start the annotation process:  
     ```bash  
     python app.py  
     ```  

3. **Parameters**  
     The script uses the following parameters:  
     - `data_path`: Path to the video prompt files.  
     - `jsonpath`: Path to store annotation files.  
     - `subdirectory`: Dataset corresponding to the selected dimension.  
     - `annokey`: Dimension to be annotated.  
     - `models`: List of models to annotate.  
     - `annos`: Reference annotations provided to assist annotators.  

4. **Annotation Workflow**  
     - The script reads prompt files from the specified `data_path`.  
     - Annotations are saved in the `jsonpath` directory.  
     - The `subdirectory` and `annokey` define the dataset and dimension for annotation.  
     - The `models` list specifies the models to be annotated.  

## Example  
To annotate videos for the `object_class` dimension using the `cogvideox5b` model:  
1. Place the prompt file in `./data4dimensions/Prompts4dimensions/object_class.txt`.  
2. Run the script:  
     ```bash  
     python app.py  
     ```  
3. The annotations will be saved in `./data4dimensions/anno_files/`.  

## Notes  
- Ensure all paths and directories exist before running the script.  
- Modify the `models` list in the script to include or exclude specific models.  

## License  
This project is licensed under the MIT License.  
