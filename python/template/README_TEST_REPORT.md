DEFAULT_TEMPLATE_1:
is the default template. it is the simplest and contains only the essential data.

DEFAULT_TEMPLATE_2:
adds to the DEFAULT_TEMPLATE_1 the possibility to insert the parameters.
To do this, you simply need to print before the final results with all the parameters that you want to insert in the report. the parameters must be printed between the "parameters" tags (inserted at the beginning and at the end). The symbol ";" it must be used to separate the various parameters, since it will be translated as an "end-line".

DEFAULT_TEMPLATE_2:
adds to the DEFAULT_TEMPLATE_2 the possibility to insert the images. To attach them, you will need to make a print with the complete path for each image you want to attach. obviously this during the test must be generated and saved locally. paths must be printed between the "image" tags (inserted at the beginning and at the end). The symbol ";" should be used to separate the various paths. the images must be printed between the parameters and the final results.