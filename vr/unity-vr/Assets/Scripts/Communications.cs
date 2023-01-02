using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System.IO.MemoryMappedFiles;
using Unity.Jobs;
using System.Threading.Tasks;
using System;

public class Communications : MonoBehaviour
{
    // Start is called before the first frame update
    private MemoryMappedFile toPythonMem;
    private MemoryMappedFile fromPythonMem;
    private Mutex toPythonMut;
    private Mutex fromPythonMut;
    void Start()
    {
        toPythonMem = MemoryMappedFile.CreateOrOpen("toPython1", 13);
        fromPythonMem = MemoryMappedFile.CreateOrOpen("toUnity", 3);
        toPythonMut = new Mutex(false, "toPythonMut1");
        fromPythonMut = new Mutex(false, "toUnityMut");
        // Action<uint, byte[], MemoryMappedFile> writeAction = write;
        // Task readTask = new Task(write);
    }
    // struct WriteJob : IJob{ // Unity Job system apparently solves race conditions? No need to put lock here? (if I have multiple writers)
    //     public void Execute(){

    //     }
    // }
    public void updateHeadRotation(Vector3 rotation){
        // toPythonMem.
    }
    public void updateHeadPosition(Vector3 position){
        byte[] buffer = new byte[12];
        Buffer.BlockCopy(BitConverter.GetBytes(position.x), 0, buffer, 0, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.y), 0, buffer, 4, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.z), 0, buffer, 8, 4);
        Task writeTask = new Task(() => write(1, buffer));
        writeTask.Start();
    }
    private void read(){
        while (true){
        }
    }
    private void write(uint location, byte[] values){
        // Debug.Log("attempting to write");
        MemoryMappedViewAccessor writeLoc = toPythonMem.CreateViewAccessor(location, values.Length);
        MemoryMappedViewAccessor readLoc = toPythonMem.CreateViewAccessor(0, 1);
        toPythonMut.WaitOne();
        // Debug.Log("acquired");
        while (readLoc.ReadSByte(0) == 1){
            // Debug.Log(readLoc.ReadSByte(0));
            toPythonMut.ReleaseMutex();
            // Debug.Log("released");
            Thread.Sleep(1);
            toPythonMut.WaitOne();
            // Debug.Log("acquired");
        }
        // Debug.Log("writing!");
        Byte one = 1;   // 8^)
        readLoc.Write(0, one);
        writeLoc.WriteArray<byte>(0, values, 0,  values.Length);
        // Debug.Log("finished writing");
        toPythonMut.ReleaseMutex();
        // Debug.Log("released");
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
