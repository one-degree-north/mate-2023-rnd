using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RenderManager : MonoBehaviour
{
    public RenderTexture background;
    public Renderer render;
    public Texture2D texture;
    int pixelNum;
    int currPhotoNum = 0;
    void Start()
    {
        render.material.mainTexture = texture;
        pixelNum = background.height * background.width;
    }
    public void testImageUpdate(){
        RenderTexture.active = background;
        if (currPhotoNum == 3){
            currPhotoNum = 0;
        }
        //Color[] pixels = null;
        Texture2D tex = null;
        switch(currPhotoNum){
            case 0:
            tex = Resources.Load<Texture2D>("ActualImageTest2");
            Debug.Log("AA");
            break;
            case 1:
            tex = Resources.Load<Texture2D>("ActualImageTest3");
            Debug.Log("BBB");
            break;
            case 2:
            tex = Resources.Load<Texture2D>("ActualImageTest1");
            Debug.Log("CCC");
            break;
        }
        if (tex != null){
            Debug.Log(background.isReadable);
            Debug.Log(tex.width);
            Debug.Log(tex.height);
            Debug.Log(tex.GetPixel(0, 0).r);
            texture.SetPixels(tex.GetPixels());
            texture.Apply();
        }
        else{
            Debug.Log("TEX IS NULL!!!");
        }
        currPhotoNum++;
        RenderTexture.active = null;
    }
    // just writing to the given file with python cv2
    public void updateView(){
        texture.SetPixels(Resources.Load<Texture2D>("viewImage").GetPixels());
        texture.Apply();
    }

    public void parseUpdateImagePacket(byte[] input){
        updateImage(parseImagePacket32(input));
    }

    Color[] parseImagePacket32(byte[] input){
        //check input len

        Color[] colors = new Color[pixelNum];
        Color currColor = new Color();
        int colorIndex = 0;
        int pixelIndex = 0;
        int colorValue = 0;
        int rgbIndex = 0;
        for (int i = 0; i < 1024; i++){
            for (int j = 0; j < 2048*3*3; j++){
                byte currBit = input[i*2048*3*3 + j];
                colorValue &= (currBit<<8*pixelIndex);
                if (pixelIndex == 3){
                    switch(rgbIndex){
                        case 0:
                        currColor.r = colorValue;
                        break;
                        case 1:
                        currColor.g = colorValue;
                        break;
                        case 2:
                        currColor.b = colorValue;
                        rgbIndex = 0;
                        colors[colorIndex] = currColor;
                        colorIndex++;
                        break;
                    }
                    rgbIndex++;
                    colorValue = 0;
                }
                pixelIndex++;
            }
        }
        return colors;
    }
    void updateImage(Color[] colors){
        RenderTexture.active = background;
        texture.SetPixels(colors);
        texture.Apply();
        RenderTexture.active = null;
    }
}
