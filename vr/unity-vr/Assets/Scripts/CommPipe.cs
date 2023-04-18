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
using System.Linq;


public class CommPipe : MonoBehaviour{
    public static byte HEADER = 0xAA;
    public static byte FOOTER = 0xBB;
    private NamedPipeClientStream fromPythonPipe;
    private NamedPipeClientStream toPythonPipe;
    // private Task readTask;
    // private Task writeTask;
    private ConcurrentQueue<InputData> writeQueue;
    private ConcurrentQueue<InputData> readQueue;
    // private Queue<InputData> writeQueue;
    // private Queue<InputData> readQueue;
    private Stream stream;
    public RectTransform canvas;
    private Thread readThread;
    private Thread writeThread;
    void Start(){
        // System.IO.Pipes.Pipe
        toPythonPipe = new NamedPipeClientStream(".", "fromUnityPipe", PipeDirection.InOut);
        fromPythonPipe = new NamedPipeClientStream(".", "toUnityPipe", PipeDirection.InOut);    // need inout for dumb readmode
        // fromPythonPipe = new NamedPipeClientStream(".", "toUnityPipe", PipeAccessRights.ReadData | PipeAccessRights.WriteAttributes, 
        //                      PipeOptions.None, 
        //                      System.Security.Principal.TokenImpersonationLevel.None, 
        //                      System.IO.HandleInheritability.None);
        // fromPythonPipe.ReadMode = PipeTransmissionMode.Message;
        fromPythonPipe.Connect();
        toPythonPipe.Connect();
        fromPythonPipe.ReadMode = PipeTransmissionMode.Message;
        // namedPipe.ReadMode = PipeTransmissionMode.Message;
        
        writeQueue = new ConcurrentQueue<InputData>();
        readQueue = new ConcurrentQueue<InputData>();
        // writeQueue = new Queue<InputData>();
        // readQueue = new Queue<InputData>();

        readThread = new Thread(new ThreadStart(readLoop));
        readThread.Start();
        writeThread = new Thread(new ThreadStart(writeLoop));
        writeThread.Start();
        // stream = new Stream(namedPipe);
        // readTask = new Task(readLoop);
        // readTask.Start();
        // Task.Run(writeLoop);
        // Task.Run(readLoop);
        // StartCoroutine(readPipe());
    }
    void readLoop(){
        while (true){
            Debug.Log("a");
            byte[] buffer = new byte[2048];
            int readNum = fromPythonPipe.Read(buffer, 0, 2048);
            Debug.Log("readed!");
            Debug.Log(readNum);
            // processReadData(new InputData(buffer, readNum));
            // Debug.Log("finish");
            readQueue.Enqueue(new InputData(buffer, readNum));
        }
    }
    public void exitApp(){

    }
    void processReadData(InputData input){
        Debug.Log("recv data");
        // Debug.Log("created InputData");
        Debug.Log(input.command);
        Debug.Log(input.data.Length);
        Debug.Log(fromPythonPipe.IsMessageComplete);
        switch (input.command){
            case 0x01:  // debug, echo
                Debug.Log(input.data);
            break;
            case 0x02:  // move camera view
                Debug.Log("moving!");
                canvas.eulerAngles = new Vector3(BitConverter.ToSingle(input.data, 0), BitConverter.ToSingle(input.data, 4), BitConverter.ToSingle(input.data, 8));
            break;
        }
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
    public void writeCurrTime(){    // sends the current time, test for latency
        byte[] buffer = BitConverter.GetBytes(DateTimeOffset.Now.ToUnixTimeMilliseconds());
        writeQueue.Enqueue(new InputData(0x0B, buffer));
    }
    public void writeData(InputData data){
    }
    void writeLoop(){
        while (true){
            InputData data;
            bool dataPresent = writeQueue.TryDequeue(out data);
            // Debug.Log("writing loop");
            // Debug.Log(writeQueue.Count);
            if (dataPresent){
                // InputData data = writeQueue.Dequeue();
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
    IEnumerator readPipe(){
        while (true){
            Debug.Log("attempting to read...");
            byte[] buffer = new byte[2048];
            // processReadData(new InputData(buffer, readNum));
            // Debug.Log("finish");
            // readQueue.Enqueue(new InputData(buffer, readNum));
            int readNum = fromPythonPipe.Read(buffer, 0, 2048);
            Debug.Log("readed!");
            Debug.Log(readNum);
            processReadData(new InputData(buffer, readNum));
            yield return null;
        }
    }
    void Update(){
        InputData inputData;
        bool dataPresent = readQueue.TryDequeue(out inputData);
        if (dataPresent){
            processReadData(inputData);
        }
        // Debug.Log("a");
        //     byte[] buffer = new byte[2048];
        //     int readNum = fromPythonPipe.Read(buffer, 0, 2048);
        //     Debug.Log("readed!");
        //     Debug.Log(readNum);
        //     processReadData(new InputData(buffer, readNum));
        // Debug.Log("a");
        //     byte[] buffer = new byte[2048];
        //     int readNum = fromPythonPipe.Read(buffer, 0, 2048);
        //     processReadData(buffer);
            // Debug.Log("finish");
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
    void OnApplicationQuit(){
        // remove read thread
        Debug.Log("exiting");
        readThread.Abort();
        writeThread.Abort();
    }
}
public class InputData{
    public byte command;
    public byte[] data;
    public byte[] returnWriteData(){
        byte[] returnData = new byte[data.Length+1];
        data.CopyTo(returnData, 1);
        // returnData[0] = CommPipe.HEADER;
        returnData[0] = command;
        // returnData[data.Length+2] = CommPipe.FOOTER;
        return returnData;
    }
    public InputData(byte command, byte[] data){
        this.command = command;
        this.data = data;
    }
    public InputData(byte[] data, int length){
        this.command = data[0];
        this.data = new byte[length - 1];
        Array.Copy(data, 1, this.data, 0, length-1);
    }
}