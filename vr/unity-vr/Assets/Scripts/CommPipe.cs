using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System.IO.MemoryMappedFiles;
using Unity.Jobs;
using System.Threading.Tasks;
using System;
using System.Collections.Concurrent;
using System.IO.Pipes;
using System.IO;

public class CommPipe : MonoBehaviour{
    public static byte HEADER = 0xAA;
    public static byte FOOTER = 0xBB;
    private NamedPipeClientStream fromPythonPipe;
    private NamedPipeClientStream toPythonPipe;
    // private Task readTask;
    // private Task writeTask;
    private Queue<InputData> writeQueue;
    private Stream stream;
    private Queue<InputData> readQueue;
    void Start(){
        toPythonPipe = new NamedPipeClientStream(".", "fromUnityPipe", PipeDirection.Out);
        fromPythonPipe = new NamedPipeClientStream(".", "toUnityPipe", PipeDirection.In);
        fromPythonPipe.Connect();
        toPythonPipe.Connect();
        // namedPipe.ReadMode = PipeTransmissionMode.Message;
        writeQueue = new Queue<InputData>();
        readQueue = new Queue<InputData>();
        // stream = new Stream(namedPipe);
        // readTask = new Task(readLoop);
        // readTask.Start();
        Task.Run(writeLoop);
        // Task.Run(readLoop);
    }
    void readLoop(){
        while (true){
            byte[] buffer = new byte[2048];
            int readNum = fromPythonPipe.Read(buffer, 0, 2048);
            processReadData(buffer);
        }
    }
    void processReadData(byte[] buffer){

    }
    public void writeData(Vector3 position){
        byte[] buffer = new byte[12];
        Buffer.BlockCopy(BitConverter.GetBytes(position.x), 0, buffer, 0, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.y), 0, buffer, 4, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.z), 0, buffer, 8, 4);
        InputData inputData = new InputData(0xEE, buffer);
        writeQueue.Enqueue(inputData);
    }
    public void writeAllData(Vector3 hSetPos, Vector3 hSetRotation, Vector4 hSetQuat, Vector3 rControlPos, Vector3 rControlRot, Vector4 rControlQuat, 
    Vector3 lControlPos, Vector3 lControlRot, Vector4 lControlQuat, float rClaw, float lClaw, float f, float s, float u, float r, float p, float y){
        float[] floats = {
            hSetPos.x, hSetPos.y, hSetPos.z, hSetRotation.x, hSetRotation.y, hSetRotation.z, hSetQuat.w, hSetQuat.x, hSetQuat.y, hSetQuat.z,
            rControlPos.x, rControlPos.y, rControlPos.z, rControlRot.x, rControlRot.y, rControlRot.z, rControlQuat.w, rControlQuat.x, rControlQuat.y, rControlQuat.z,
            lControlPos.x, lControlPos.y, lControlPos.z, lControlRot.x, lControlRot.y, lControlRot.z, lControlQuat.w, lControlQuat.x, lControlQuat.y, lControlQuat.z,
            rClaw, lClaw, f, s, u, r, p, y
        };
        byte[] buffer = new byte[floats.Length*4];
        for (int i = 0; i < floats.Length; i++){
            Buffer.BlockCopy(BitConverter.GetBytes(floats[i]), 0, buffer, i*4, 4);
        }
        writeQueue.Enqueue(new InputData(0x0A, buffer));
    }
    void writeLoop(){
        while (true){
            if (writeQueue.Count > 0){
                InputData data = writeQueue.Dequeue();
                // Debug.Log("writing");
                // Debug.Log(string.Join(", ", data.returnWriteData()));
                // Debug.Log(data.returnWriteData());
                byte[] buffer = (byte[])data.returnWriteData().Clone();
                // Debug.Log(namedPipe.CanWrite);
                toPythonPipe.Write(buffer);
                // Debug.Log("A");
                // try{
                //     namedPipe.Write(data.returnWriteData());
                // }
                // catch (Exception e){
                //     Debug.Log(e.ToString());
                // }
            }
        }
    }
    void Update(){
        // Debug.Log("count: ");
        // Debug.Log(writeQueue.Count);
        // if (writeQueue.Count > 0){
        //         InputData data = writeQueue.Dequeue();
        //         Debug.Log("writing");
        //         Debug.Log(string.Join(", ", data.returnWriteData()));
        //         // Debug.Log(data.returnWriteData());
        //         byte[] buffer = (byte[])data.returnWriteData().Clone();
        //         Debug.Log(namedPipe.CanWrite);
        //         namedPipe.Write(buffer);
        //         Debug.Log("A");
        //         try{
        //             namedPipe.Write(data.returnWriteData());
        //         }
        //         catch (Exception e){
        //             Debug.Log(e.ToString());
        //         }
        //     }
    }
}
public class InputData{
    public byte command;
    public byte[] data;
    public byte[] returnWriteData(){
        byte[] returnData = new byte[data.Length+3];
        data.CopyTo(returnData, 2);
        returnData[0] = CommPipe.HEADER;
        returnData[1] = command;
        returnData[data.Length+2] = CommPipe.FOOTER;
        return returnData;
    }
    public InputData(byte command, byte[] data){
        this.command = command;
        this.data = data;
    }
}