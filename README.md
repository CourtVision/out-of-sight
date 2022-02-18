# `out-of-sight`:eyes:
## This is a pet project for fun :blush:
- using CV & NLP 
    - to recognize & anonymize license plates 
    - and search having a functionality within a whitlelist DB
#### Main purpose is to create a containarized Python app with decomposed tasks and a flexible workflow.
#### Most of the CV & NLP code is based on from Adrian Rosebrock´s blog posts on PyImageSearch[^1]

## Main tasks executed by [`app.py`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/app.py):
- :world_map:[`Locator`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/locator.py): finds license plate like rectangles on the input image
- :eye_speech_bubble:[`Reader`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/reader.py): performs OCR on the image segment in question
- :framed_picture:[`Display`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/display.py): Persists the image with the superimposed text of the license plate
- :see_no_evil:[`Anonymizer`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/anonymizer.py): blurs the license plate 
- :scroll:[`Searcher`](https://github.com/CourtVision/out-of-sight/blob/main/outsight/utils/searcher.py): checks the given license plate´s text in a list of whitlisted plates with an arbitrary degree of similarity

## Docker container
- Takes a mounted input/output volume (defined in a [`CONFIG.yaml`](https://github.com/CourtVision/out-of-sight/blob/main/CONFIG.yaml)) with the image and (an optional) whitelist of license plates
- Arguments include:
    -  task(s) to be executed (`-w`)
    -  threshold for the Levensthein distance of the whitelist comparision (`-t`)
    -  pixelization parameter for the anonymization task (`-b`)
    -  switch for debugging (`--no-debug`)

## Workflow execution with [`d6tflow`](https://github.com/d6t/d6tflow)
- Given a successful localization
    - the other tasks can be executed independently
    - governed by the above Python arguments in the `docker run` command

## Basic usage
`docker run -v io-volume:/./io --name outsight-container outsight-image -w all --no-debug`

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
- Get Tesseract work in Docker (locally no problem)
- Finish pdoc 

## License
[License](https://github.com/CourtVision/out-of-sight/blob/main/outsight/LICENSE)


[^1]: Tutorials in blog posts of Adrian Rosebrock - PyImageSearch (accessed: 07.02.2022)
      - https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/
      - https://www.pyimagesearch.com/2019/12/02/opencv-vehicle-detection-tracking-and-speed-estimation/
      - https://www.pyimagesearch.com/2020/04/06/blur-and-anonymize-faces-with-opencv-and-python/
      - https://www.pyimagesearch.com/2020/09/21/opencv-automatic-license-number-plate-recognition-anpr-with-python/
