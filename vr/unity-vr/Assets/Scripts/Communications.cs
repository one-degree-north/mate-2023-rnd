using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System.IO.MemoryMappedFiles;
using Unity.Jobs;
using System.Threading.Tasks;
using System;
using System.Collections.Concurrent;

public class Communications : MonoBehaviour
{
    // Start is called before the first frame update
    private MemoryMappedFile toPythonMem;
    private MemoryMappedFile fromPythonMem;
    private Mutex toPythonMut;
    private Mutex fromPythonMut;
    private ConcurrentQueue<WriteInput> writeQueue = new ConcurrentQueue<WriteInput>();
    private static int MAX_READ_LENGTH = 1000;
    private static int MAX_WRITE_LENGTH = 1000;
    private Task writeLoopTask;
    private Task readTask;
    public readonly object exitLock = new object();
    public bool exit = false;
    void Start()
    {
        toPythonMem = MemoryMappedFile.CreateOrOpen("toPython1", MAX_WRITE_LENGTH);
        fromPythonMem = MemoryMappedFile.CreateOrOpen("toUnity", MAX_READ_LENGTH);
        toPythonMut = new Mutex(false, "toPythonMut1");
        fromPythonMut = new Mutex(false, "toUnityMut");
        // Action<uint, byte[], MemoryMappedFile> writeAction = write;
        // Task readTask = new Task(write);
        writeLoopTask = new Task(writeLoop);
        writeLoopTask.Start();
        readTask = new Task(readLoop);
        readTask.Start();
    }
    // struct WriteJob : IJob{ // Unity Job system apparently solves race conditions? No need to put lock here? (if I have multiple writers)
    //     public void Execute(){

    //     }
    // }
    public void exitApp(){
        // remove locks!
        Debug.Log("exiting!");
        lock(exitLock){
            exit = true;
        }
        // writeLoopTask.Wait();
        // readTask.Wait();
        // now it's safe to exit!

        // Application.Quit();
    }
    public void writeExit(){
        writeQueue.Enqueue(new WriteInput(0x10, new byte[0]));
    }
    public void updateMoveForward(float degree){
        updateMove(0x20, degree);
    }
    public void updateMoveSide(float degree){
        updateMove(0x21, degree);
    }
    public void updateMoveUp(float degree){
        updateMove(0x22, degree);
    }
    public void updateRoll(float degree){
        updateMove(0x23, degree);
    }
    public void updatePitch(float degree){
        updateMove(0x24, degree);
    }
    public void updateYaw(float degree){
        updateMove(0x25, degree);
    }
    private void updateMove(byte command, float degree){
        byte[] buffer = new byte[4];
        Buffer.BlockCopy(BitConverter.GetBytes(degree), 0, buffer, 0, 4);
        writeQueue.Enqueue(new WriteInput(command, buffer));
    }
    public void updateHeadRotation(Vector3 rotation){
        byte[] buffer = new byte[12];
        Buffer.BlockCopy(BitConverter.GetBytes(rotation.x), 0, buffer, 0, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(rotation.y), 0, buffer, 4, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(rotation.z), 0, buffer, 8, 4);
        // Task writeTask = new Task(() => write(1, buffer));
        // writeTask.Start();
        writeQueue.Enqueue(new WriteInput(0x03, buffer));
    }
    public void updateHeadPosition(Vector3 position){
        byte[] buffer = new byte[12];
        Buffer.BlockCopy(BitConverter.GetBytes(position.x), 0, buffer, 0, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.y), 0, buffer, 4, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.z), 0, buffer, 8, 4);
        // Task writeTask = new Task(() => write(1, buffer));
        // writeTask.Start();
        writeQueue.Enqueue(new WriteInput(0x02, buffer));
    }
    private void readLoop(){
        while (true){
            MemoryMappedViewAccessor memAccess = fromPythonMem.CreateViewAccessor(0, MAX_READ_LENGTH);
            toPythonMut.WaitOne();
            while (memAccess.ReadSByte(0) == 0){
                toPythonMut.ReleaseMutex();
                Thread.Sleep(1);
                toPythonMut.WaitOne();
            }


            // while (memAccess.ReadSByte(0) == 0){
            //     Thread.Sleep(1);
            // }
            // toPythonMut.WaitOne();



            // Byte one = 1;   // 8^) this is dumb but whatever.
            memAccess.Write(0, (Byte) 0);
            byte command = memAccess.ReadByte(1);
            switch (command){
                case 0x02: // image
                break;
                case 0x10:  // closed connection
                // exit = true;
                break;
                case 0x11:  // stopp reading
                break;
            }
            // read and interperate values
            // settings

            // image rotation

            // image values
            
            toPythonMut.ReleaseMutex();
            // Debug.Log("released");
            lock(exitLock){
                if (exit){
                    Debug.Log("EXIT!");
                    break;
                }
            }
        }
    }
    private void writeLoop(){
        while (true){
            WriteInput currInput;
            if (writeQueue.TryDequeue(out currInput)){
                write(currInput.command, currInput.data);
                lock (exitLock){
                    if (exit){
                        Debug.Log("EXIT WRITE!");
                        break;
                    }
                }
            }
        }
    }
    private bool write(byte command, byte[] values){
        // Debug.Log("writing");
        MemoryMappedViewAccessor memAccess = toPythonMem.CreateViewAccessor(0, MAX_WRITE_LENGTH);
        toPythonMut.WaitOne();
        // Debug.Log("acquired");
        while (memAccess.ReadSByte(0) == 1){
            // Debug.Log(readLoc.ReadSByte(0));
            toPythonMut.ReleaseMutex();
            // Debug.Log("released");

            // Thread.Sleep(1);

            toPythonMut.WaitOne();
            // Debug.Log("acquired");
        }
        // Debug.Log("writing!");
        memAccess.Write(0, (byte) 1);
        memAccess.Write(1, command);
        // Debug.Log(values.Length);
        memAccess.WriteArray<byte>(2, values, 0,  values.Length);
        // Debug.Log("finished writing");
        toPythonMut.ReleaseMutex();
        // Debug.Log("released");
        return command == 0x10; // exit!!
    }
    void Update(){
        Debug.Log("queue count: ");
        Debug.Log(writeQueue.Count);
    }
}
public class WriteInput{
    public byte command;
    public byte[] data;
    public WriteInput(byte command, byte[] data){
        this.command = command;
        this.data = data;
    }
}