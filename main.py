from OpenCVPPL import OpenCVPPL

if __name__ == "__main__":
    app = OpenCVPPL()

    #app.file_open("images/img800x600.png")
    #app.file_open("images/buho.jpg")
    app.file_open("images/chaplin-noisy.png")
    app.file_open("images/cebra.jpg")
    #app.file_open("c:/Zip/mimo-mu-mimo.jpg")
    app.file_open("images/korea.jpg")


    app.mainloop()