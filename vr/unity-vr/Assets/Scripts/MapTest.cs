using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System.IO.MemoryMappedFiles;
using Unity.Jobs;
using System.Threading.Tasks;
using System;

public class MapTest : MonoBehaviour
{
    // Start is called before the first frame update
    private MemoryMappedFile toPythonMem;
    public Communications comms;
    Vector3 pos = new Vector3(0, 0, 0);
    void Start()
    {
        toPythonMem = MemoryMappedFile.CreateOrOpen("toPython1", 13);
    }
    private void write(Vector3 position){
        byte[] buffer = new byte[12];
        Buffer.BlockCopy(BitConverter.GetBytes(position.x), 0, buffer, 0, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.y), 0, buffer, 4, 4);
        Buffer.BlockCopy(BitConverter.GetBytes(position.z), 0, buffer, 8, 4);

        MemoryMappedViewAccessor writeLoc = toPythonMem.CreateViewAccessor(1, buffer.Length);
        MemoryMappedViewAccessor readLoc = toPythonMem.CreateViewAccessor(0, 1);
        Byte val = 1;
        readLoc.Write(0, val);
        readLoc.Write(13, val);
        writeLoc.WriteArray(0, buffer, 0,  buffer.Length);
        Debug.Log("update map");
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.A)){
            pos.x ++;
            comms.updateHeadPosition(pos);
        }
    }
}
