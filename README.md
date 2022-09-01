# epub-to-audio
Convert books from Project Gutenberg to audio using cloud text-to-speech.

Currently only uses Google's platform. 

## How to use
Create a folder named "input" in the project's root directory. Put epubs in that folder, and run the script. No arguments needed/supported. It will parse each book, try to separate them into chapters, and send them off to the cloud to be translated. Response is put into "output" folder.
## Google
Initial setup must be done according to the "Getting Started" page [here](https://cloud.google.com/text-to-speech/docs/before-you-begin?hl=en_US). The key should be placed in a .secrets folder in the project's root directory.
<i>Note: <u>This is not a free service!</u></i> Although Google does give a generous credit to the account when first joining.
## Amazon
Not implemented.
## Local
Not implemented.