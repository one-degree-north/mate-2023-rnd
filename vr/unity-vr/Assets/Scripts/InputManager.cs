using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using System;
using System.Buffers.Binary;
public class InputManager : MonoBehaviour
{
    public SteamVR_Action_Vector2 moveForwardSide;
    public SteamVR_Action_Vector2 moveUpRoll;
    public SteamVR_Action_Single moveRightClaw;
    public SteamVR_Action_Single moveLeftClaw;
    public SteamVR_Action_Single yaw;
    public SteamVR_Action_Boolean yawUp;
    public SteamVR_Action_Boolean yawDown;
    public SteamVR_Action_Single pitch;
    public SteamVR_Action_Pose headPos;
    public NetworkTest networkTest;
    public Transform headTransform;
    public Vector3 pastRotation;
    public Vector3 pastPosition;
    void Start()
    {
        moveForwardSide.AddOnChangeListener(sendForwardSide, SteamVR_Input_Sources.Any);
        // headPos.AddOnChangeListener(SteamVR_Input_Sources.Any, sendHeadPos);
        pastRotation = headTransform.localEulerAngles;
    }
    // public void sendHeadPos(SteamVR_Action_Pose headPos, SteamVR_Input_Sources source){
    //     Debug.Log("head transform changed");
    //     byte[] output = new byte[25];
    //     output[0] = 0x01;
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.x), 0, output, 1, 4);
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.y), 0, output, 5, 4);
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.z), 0, output, 9, 4);
    //     Debug.Log(output.ToString());
    //     networkTest.writeQueue.Enqueue(output);
    //     output[0] = 0x02;
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.x), 0, output, 1, 4);
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.y), 0, output, 5, 4);
    //     Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.z), 0, output, 9, 4);
    //     Debug.Log(output.ToString());
    //     networkTest.writeQueue.Enqueue(output);
    // }
    void sendHeadPos(Transform headPos){
        Debug.Log("head transform changed");
        byte[] output = new byte[25];
        output[0] = 0x01;
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.x), 0, output, 1, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.y), 0, output, 5, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localPosition.z), 0, output, 9, 4);
        Debug.Log(output.ToString());
        networkTest.writeQueue.Enqueue(output);
        output[0] = 0x02;
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.x), 0, output, 1, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.y), 0, output, 5, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.z), 0, output, 9, 4);
        Debug.Log(output.ToString());
        networkTest.writeQueue.Enqueue(output);
    }

    void sendForwardSide(SteamVR_Action_Vector2 forwardSide, SteamVR_Input_Sources source, Vector2 axis, Vector2 delta){
        Debug.Log("moving forward");
    }
    void Update(){
        // 
        if (!pastRotation.Equals(headTransform.localEulerAngles)){
            Vector3 currRotation = headTransform.localEulerAngles;
            byte[] output = new byte[13];
            output[0] = 0x03;
            Buffer.BlockCopy(BitConverter.GetBytes(currRotation.x), 0, output, 1, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(currRotation.y), 0, output, 5, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(currRotation.z), 0, output, 9, 4);
            
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.x), 0, output, 13, 4);
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.y), 0, output, 17, 4);
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.z), 0, output, 21, 4);
            // Array.Reverse(output);  //convert to big-endian
            // for (int i = 0; i < 13; i++){
            //     Debug.Log(output[i]);
            // }
            networkTest.writeQueue.Enqueue(output);
            // Debug.Log(headTransform.localEulerAngles);
        }
        pastRotation = headTransform.localEulerAngles;
        if (!pastPosition.Equals(headTransform.localPosition)){
            Vector3 currPosition = headTransform.localPosition;
            byte[] output = new byte[13];
            output[0] = 0x02;
            Buffer.BlockCopy(BitConverter.GetBytes(currPosition.x), 0, output, 1, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(currPosition.y), 0, output, 5, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(currPosition.z), 0, output, 9, 4);
            
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.x), 0, output, 13, 4);
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.y), 0, output, 17, 4);
            // Buffer.BlockCopy(BitConverter.GetBytes(headPos.localRotation.z), 0, output, 21, 4);
            // Array.Reverse(output);  //convert to big-endian
            // for (int i = 0; i < 13; i++){
            //     Debug.Log(output[i]);
            // }
            networkTest.writeQueue.Enqueue(output);
            // Debug.Log(currPosition);
        }
        pastPosition = headTransform.localPosition;
    }
}
