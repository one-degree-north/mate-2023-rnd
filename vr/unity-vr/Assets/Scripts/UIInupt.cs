using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.Extras;

public class UIInupt : MonoBehaviour
{
    // Start is called before the first frame update
    public SteamVR_LaserPointer laserPointer;
    public Communications comms;
    void Start()
    {
        laserPointer.PointerIn += pointerClicked;
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
