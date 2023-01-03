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
    void Start()
    {
        toPythonMem = MemoryMappedFile.CreateOrOpen("toPython1", 14);
        fromPythonMem = MemoryMappedFile.CreateOrOpen("toUnity", 3);
        toPythonMut = new Mutex(false, "toPythonMut1");
        fromPythonMut = new Mutex(false, "toUnityMut");
        // Action<uint, byte[], MemoryMappedFile> writeAction = write;
        // Task readTask = new Task(write);
        Task writeLoopTask = new Task(writeLoop);
        writeLoopTask.Start();
    }
    // struct WriteJob : IJob{ // Unity Job system apparently solves race conditions? No need to put lock here? (if I have multiple writers)
    //     public void Execute(){

    //     }
    // }
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
            // try to read
        // MemoryMappedViewAccessor writeLoc = toPythonMem.CreateViewAccessor(location, values.Length);
        // MemoryMappedViewAccessor readLoc = toPythonMem.CreateViewAccessor(0, 1);
        MemoryMappedViewAccessor memAccess = fromPythonMem.CreateViewAccessor(0, 3);
        toPythonMut.WaitOne();
        // Debug.Log("acquired");
        while (memAccess.ReadSByte(0) == 1){
            // Debug.Log(readLoc.ReadSByte(0));
            toPythonMut.ReleaseMutex();
            // Debug.Log("released");
            Thread.Sleep(1);
            toPythonMut.WaitOne();
            // Debug.Log("acquired");
        }
        // Byte one = 1;   // 8^) this is dumb but whatever.
        memAccess.Write(0, (Byte) 1);
        // read and interperate values
        // settings


        // image rotation


        // image values
        

        toPythonMut.ReleaseMutex();
        // Debug.Log("released");
        }
    }
    private void writeLoop(){
        while (true){
            WriteInput currInput;
            if (writeQueue.TryDequeue(out currInput)){
                write(currInput.command, currInput.data);
            }
        }
    }
    private void write(byte command, byte[] values){
        // Debug.Log("attempting to write");
        // MemoryMappedViewAccessor writeLoc = toPythonMem.CreateViewAccessor(location, values.Length);
        // MemoryMappedViewAccessor readLoc = toPythonMem.CreateViewAccessor(0, 1);
        Debug.Log("writing");
        MemoryMappedViewAccessor memAccess = toPythonMem.CreateViewAccessor(0, 14);
        toPythonMut.WaitOne();
        Debug.Log("acquired");
        while (memAccess.ReadSByte(0) == 1){
            // Debug.Log(readLoc.ReadSByte(0));
            toPythonMut.ReleaseMutex();
            Debug.Log("released");
            Thread.Sleep(1);
            toPythonMut.WaitOne();
            Debug.Log("acquired");
        }
        Debug.Log("writing!");
        Byte one = 1;   // 8^)
        memAccess.Write(0, one);
        memAccess.Write(1, command);
        Debug.Log(values.Length);
        memAccess.WriteArray<byte>(2, values, 0,  values.Length);
        // Debug.Log("finished writing");
        toPythonMut.ReleaseMutex();
        // Debug.Log("released");
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