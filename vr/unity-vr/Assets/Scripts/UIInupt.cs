using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.Extras;
using UnityEngine.Windows.WebCam;

public class UIInupt : MonoBehaviour
{
    // Start is called before the first frame update
    public SteamVR_LaserPointer laserPointer;
    public CommPipe comms;

    private PhotoCapture photoCapture;
    private WebCamTexture webTex;
    private int imgHeight;
    private int imgWidth;
    private WebCamDevice[] devices;
    public RawImage rawImage;

    void Start()
    {
        laserPointer.PointerIn += pointerClicked;

        WebCamDevice[] devices = WebCamTexture.devices;
        // foreach (WebCamDevice dev in devices){
        //     Debug.Log(dev.name);
        // }
        if (devices.Length != 0){
        // webTex = new WebCamTexture(devices[0].name);
        // Debug.Log(devices[0].name);
        // rawImage.texture = webTex;
        // webTex.Play();
        }
        // rawImage.texture = webTex;
        // webTex = new WebCamTexture(devices[0].name);
        // webTex.Play();
    }

    // Update is called once per frame
    private void pointerClicked(object sender, PointerEventArgs e){
        switch (e.target.name){
            case "exitButton":
                comms.exitApp();
            break;
        }
    }
}
