using System.Collections;
using System.Collections.Generic;
using UnityEngine;
// using OpenCvSharp;
// using OpenCvSharp.Utilities;
// using OpenCvSharp.Extensions;
using System.Runtime.InteropServices;
// using System.Drawing;
// using OpenCvSharp.
using System.Linq;
using UnityEngine.Windows.WebCam;
using UnityEngine.UI;

public class CameraInput : MonoBehaviour
{
    // Start is called before the first frame update
    private PhotoCapture photoCapture;
    private WebCamTexture webTex;
    private int imgHeight;
    private int imgWidth;
    private WebCamDevice[] devices;
    // private Mat imgMat;
    // private Texture2D tex;
    // public RenderTexture renderTexture;
    // public Renderer render;
    public RawImage rawImage;
    // public Image image;
    void Start()
    {
        WebCamDevice[] devices = WebCamTexture.devices;
        foreach (WebCamDevice dev in devices){
            Debug.Log(dev.name);
        }
        Debug.Log(devices[0].name);
        webTex = new WebCamTexture(devices[0].name);
        rawImage.texture = webTex;
        // webTex = new WebCamTexture(devices[0].name);
        webTex.Play();
        // Resolution cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();
        // renderTexture.height = cameraResolution.height;
        // renderTexture.width = cameraResolution.width;
        // foreach (Resolution res in PhotoCapture.SupportedResolutions){
        //     Debug.Log("---");
        //     Debug.Log(res.refreshRate);
        //     Debug.Log(res.width);
        //     Debug.Log(res.height);
        // }
        // tex = new Texture2D(cameraResolution.width, cameraResolution.height);
        // // render.material.mainTexture = tex;
        // // render.material.mainTexture = tex;
        // image.material.mainTexture = tex;

        // PhotoCapture.CreateAsync(false, delegate(PhotoCapture captureObject){
        //     photoCapture = captureObject;
        //     CameraParameters cameraParameters = new CameraParameters();
        //     // cameraParameters.cameraResolutionHeight = camera
        //     cameraParameters.pixelFormat = CapturePixelFormat.BGRA32;
        //     cameraParameters.cameraResolutionHeight = cameraResolution.height;
        //     cameraParameters.cameraResolutionWidth = cameraResolution.width;
        //     photoCapture.StartPhotoModeAsync(cameraParameters, delegate(PhotoCapture.PhotoCaptureResult result){
        //         photoCapture.TakePhotoAsync(CapturePhoto);
        //     });
        // });


        // cam = new VideoCapture(0);
        // cam.Open(0);
        // imgMat = new Mat();
    }

    // void CapturePhoto(PhotoCapture.PhotoCaptureResult result, PhotoCaptureFrame photoCaptureFrame){
    //     RenderTexture.active = renderTexture;
    //     // Debug.Log(photoCaptureFrame)
    //     photoCaptureFrame.UploadImageDataToTexture(tex);
    //     // Debug.Log(tex.GetPixel(3, 3));
    //     // tex.Apply();
    //     // Debug.Log(tex.GetPixel(3, 3));
    //     // RenderTexture.active = renderTexture;
    //     // renderTexture.active = null;
    //     RenderTexture.active = null;
    //     photoCapture.TakePhotoAsync(CapturePhoto);
    // }

    // Update is called once per frame
    void Update()
    {

        // cam.Read(imgMat);
        // // Debug.Log(imgMat.);
        // byte[] matData = new byte[imgHeight*imgWidth*3];
        // imgMat.GetArray(out matData);
        // Color32[] colorArr = new Color32[imgHeight*imgWidth];
        // for (int i = 0; i < imgWidth; i++){
        //     for (int j = 0; j < imgHeight; j++){
        //         colorArr[i*imgWidth+j] = new Color32(matData[i*imgWidth*3+j*3], matData[i*imgWidth*3+j*3+1], matData[i*imgWidth*3+j*3+2], 0);
        //     }
        // }
        // RenderTexture.active = renderTexture;
        // tex.SetPixels32(colorArr);
        // tex.Apply();
        // RenderTexture.active = null;
        // // imgMat.Release();
    
    }
}
