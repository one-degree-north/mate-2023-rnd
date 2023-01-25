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
    // public SteamVR_Action_Single moveForward;
    // public SteamVR_Action_Single moveSide;
    // public SteamVR_Action_Single moveUp;
    // public SteamVR_Action_Single roll;
    public SteamVR_Action_Single pitch;
    public SteamVR_Action_Single yawR;
    public SteamVR_Action_Single yawL;
    public SteamVR_Action_Pose handPosR;
    public SteamVR_Action_Pose handPosL;
    public SteamVR_Action_Single moveRightClaw;
    public SteamVR_Action_Single moveLeftClaw;
    public SteamVR_Action_Boolean moveUp;
    public SteamVR_Action_Boolean moveDown;
    public SteamVR_Action_Pose headPos;
    public bool headRotation;   // use head to rotate rov
    public bool headUp; // use head to move rov up or down
    // public Communications comms;
    public CommPipe commPipe;
    public Transform headTransform;
    public Vector3 pastRotation;
    public Vector3 pastPosition;
    public static int SEND_DELAY = 10;  // milliseconds
    private float sendClock = 0;  // for fixed update time
    private bool[] sendReady = new bool[5]; // for fixed update time. probably a better way to do this
    void Start()
    {
        // moveForwardSide.AddOnChangeListener(sendForwardSide, SteamVR_Input_Sources.Any);
        // yawR.AddOnChangeListener(sendYaw, SteamVR_Input_Sources.Any);
        // yawL.AddOnChangeListener(sendYaw, SteamVR_Input_Sources.Any);
        // moveUpRoll.AddOnChangeListener(sendUpRoll, SteamVR_Input_Sources.Any);
        // headPos.AddOnChangeListener(SteamVR_Input_Sources.Any, headPosChange);
        // pastRotation = headTransform.localEulerAngles;
    }
    /*
    void sendForward(SteamVR_Action_Single forward, SteamVR_Input_Sources source, Single newAxis, Single delta){

    }

    void sendForwardSide(SteamVR_Action_Vector2 forwardSide, SteamVR_Input_Sources source, Vector2 axis, Vector2 delta){
        if (sendReady[0] || axis.y == 0 || axis.x == 0){
            comms.updateMoveForward(axis.y);
            comms.updateMoveSide(axis.x);
            sendReady[0] = false;
        }
    }
    void sendUpRoll(SteamVR_Action_Vector2 forwardSide, SteamVR_Input_Sources source, Vector2 axis, Vector2 delta){
        if (sendReady[1] || axis.x == 0 || axis.y == 0){
            comms.updateMoveUp(axis.y);
            comms.updateRoll(axis.x);
            sendReady[1] = false;
        }
    }
    void sendYaw(SteamVR_Action_Single forward, SteamVR_Input_Sources source, Single newAxis, Single delta){
        if (sendReady[2] || newAxis == 0){
            comms.updateYaw(yawR.axis - yawL.axis);
            sendReady[2] = false;
        }
    }
    void headPosChange(SteamVR_Action_Pose headPos, SteamVR_Input_Sources source){
        if (headRotation){
            Vector3 rotation = headPos.localRotation.eulerAngles;
            comms.updatePitch(rotation[0]);
            comms.updateRoll(rotation[1]);
            comms.updateYaw(rotation[2]);
        }
        if (headUp){
            Vector3 headPosition = headPos.localPosition;
            comms.updateMoveUp(headPosition.y);
        }
        comms.updateHeadPosition(headPos.localRotation.eulerAngles);
        comms.updateHeadRotation(headPos.localPosition);
    }*/
    void Update(){
        if ((sendClock -= Time.deltaTime * 1000) < 0){
            sendClock = SEND_DELAY + sendClock;
            commPipe.writeAllData(headTransform.localPosition, headTransform.localEulerAngles, new Vector4(headTransform.rotation.w, headTransform.rotation.x, headTransform.rotation.y, headTransform.rotation.z),
            handPosR.lastLocalPosition, handPosR.lastLocalRotation.eulerAngles, new Vector4(handPosR.lastLocalRotation.w, handPosR.lastLocalRotation.x, handPosR.lastLocalRotation.y, handPosR.lastLocalRotation.z),
            handPosL.lastLocalPosition, handPosL.lastLocalRotation.eulerAngles, new Vector4(handPosL.lastLocalRotation.w, handPosL.lastLocalRotation.x, handPosL.lastLocalRotation.y, handPosL.lastLocalRotation.z),
            moveRightClaw.axis, moveLeftClaw.axis, moveForwardSide.lastAxis.x, moveForwardSide.lastAxis.y, moveUpRoll.axis.y, moveUpRoll.axis.x, pitch.axis, (yawR.axis - yawL.axis)
            );
        }
    }
}
