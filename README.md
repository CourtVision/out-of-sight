# `out-of-sight`:eyes:
## This is a pet project for fun :blush:
- Using CV & NLP 
    - to recognize & anonymize license plates 
    - and to search, find, and match the plate text within a whitlelist DB.
- Main purpose is to create a containarized Python app with decomposed tasks and a flexible workflow.
    - Most of the CV & NLP code is based on from Adrian Rosebrock´s blog posts on PyImageSearch.[^1]
    - The license plate locator part is based on Simon Kiruri´s post.[^2]

## Main tasks executed by [`app.py`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/app.py):
- :world_map:[`Locator`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/locator.py): finds "license plate like" rectangles on the input image
- :eye_speech_bubble:[`Reader`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/reader.py): performs OCR on the image segment in question
- :framed_picture:[`Display`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/display.py): persists the image with the superimposed text of the license plate
- :see_no_evil:[`Anonymizer`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/anonymizer.py): blurs the license plate 
- :scroll:[`Searcher`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/searcher.py): checks the given license plate´s text in a list of whitlisted plates with an arbitrary degree of similarity

## Workflow execution with [`d6tflow`](https://github.com/d6t/d6tflow)
- Given a successful localization
    - the other tasks can be executed independently
    - governed by the above Python arguments in the `docker run` command
![Workflow](/readme_assets/workflow.png)

## Docker container
- Takes a mounted input/output volume (defined in a [`CONFIG.yaml`](https://github.com/CourtVision/out-of-sight/blob/main/CONFIG.yaml)) with the image and (an optional) whitelist of license plates
- Arguments include:
    -  task(s) to be executed (`-w`), `choices=['all', 'OCR', 'Whitelist', 'Anonymize']`
    -  minimum aspect ratio used to detect and filter rectangular license plates (`-minAR`), `default=2`
    -  maximum aspect ratio used to detect and filter rectangular license plates (`-maxAR`), `default=8`
    -  threshold for the Levensthein distance of the whitelist comparision (`-t`), `default = 1`
    -  distance measure during the whitelist search (`-m`), `default = 'Levensthein'`
    -  pixelization parameter , # of blocks for the blurring method (`-b`), `default = 20`
    -  switch for debugging (`default = --no-debug`)

## Basic usage
- `docker build -f Dockerfile -t outsight-image --no-cache .`
- `docker run -v io-volume:/./io --name outsight-container outsight-image -w all --no-debug`

## Future Azure Architecture
![Azure Architecture](/readme_assets/architecture.png)
#### This section is baed on the blog posts of Johan Hostens[^3] & Dr Basim Majeed[^4]

- After building the Docker image of the Python script, the second step involves registering and uploading the container image with the Azure Container Registry. 
The third step is about building the workflow using Azure Logic Apps. With the recent addition of Container Instance Group connectors, Logic Apps can control the creation of a Container Instances inside container groups, monitor the container state to detect success of execution and then delete the container and the associated container group. By ensuring that the container is only active for the amount of time necessary to complete the task, charges are minimised.

- There are many trigger types that can be used to start the Logic App including webhooks, http notifications and timed events, allowing the workflow to integrate the Python script execution with external events. When the Logic App receives the trigger event it creates a Container Group and a Container inside the group based on the image retrieved from the registry. A loop is then started that monitors the state of the Container Group until it has succeeded (indicating that the Python script has completed). The last step is to delete the Container Group.[^3] 

- We’ll use an Azure key vault to store the primary key of storage account and a managed identity to authenticate the Azure Container Instance with the key vault. During local development, we’ll use environment variables for authentication. The Azure file share will be mounted in the container. The files within this file share will appear as if they were local. It is important to know that files within an ACI are not persistent, but can be made persistent by mounting an Azure file share and storing the files in the mounted directory.[^4]

## Module documentation
[`Docs`](https://rawcdn.githack.com/CourtVision/out-of-sight/master/outsight/docs/index.html)

## Environment setup
#### if Windows:
    - Install Bash for Git
    - Install make
        - Download make-4.2.1-without-guile-w32-bin.zip (https://sourceforge.net/projects/ezwinports/files/)
        - Extract zip
        - Copy the contents to C:\ProgramFiles\Git\mingw64\ merging the folders, but do NOT overwrite/replace any exisiting files    
    - Install Miniconda & VSCode (with extensions: Python & Docker)
    - Install Tesseract (https://medium.com/quantrium-tech/installing-and-using-tesseract-4-on-windows-10-4f7930313f82)
    - Set syspaths: C:\ProgramData\Miniconda3, C:\ProgramData\Miniconda3\Scripts, C:\ProgramData\Miniconda3\Library\bin, C:\ProgramData\Tesseract-OCR
#### if Linux:
    - See the ['Dockerfile'](https://github.com/CourtVision/out-of-sight/blob/main/Dockerfile)

## TODO
- Test some other input images --> done: https://makeml.app/datasets/cars-license-plates
- Maybe in the future, experiment with Deep Learning based object detection methods.

## License
[License](https://github.com/CourtVision/out-of-sight/blob/main/outsight/LICENSE)

## References
[^1]: Tutorials in blog posts of Adrian Rosebrock - PyImageSearch (accessed: 07.02.2022)
      - https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/
      - https://www.pyimagesearch.com/2019/12/02/opencv-vehicle-detection-tracking-and-speed-estimation/
      - https://www.pyimagesearch.com/2020/04/06/blur-and-anonymize-faces-with-opencv-and-python/
      - https://www.pyimagesearch.com/2020/09/21/opencv-automatic-license-number-plate-recognition-anpr-with-python/

[^2]: License Plate Detection And Recognition Using OpenCv And Pytesseract (accessed: 07.03.2022)
      -  https://www.section.io/engineering-education/license-plate-detection-and-recognition-using-opencv-and-pytesseract/

[^3]: Running Python scripts on demand with Azure Container Instances and Azure Logic Apps (accessed: 14.03.2022)
      -  https://cloudblogs.microsoft.com/industry-blog/en-gb/technetuk/2020/02/27/running-python-scripts-on-demand-with-azure-container-instances-and-azure-logic-apps/

[^4]: Running python scripts on azure with azure container instances (accessed: 14.03.2022)
      - https://kohera.be/tutorials-2/running-python-scripts-on-azure-with-azure-container-instances/
