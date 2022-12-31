using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System;

public class NetworkTest : MonoBehaviour
{
    // Start is called before the first frame update
    public RenderManager renderManager;
    Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
    // UdpClient 
    IPEndPoint vrEndPoint;
    IPEndPoint userEndPoint;
    byte[] readBuff = new byte[10000];
    byte[] writeBuff = new byte[1000];
    byte[] testSend;
    bool connected = false;
    int connectDelayMs = 1000;
    int currConnectDelay = 1000;
    public Queue<byte[]> readQueue = new Queue<byte[]>();
    public Queue<byte[]> writeQueue = new Queue<byte[]>();
    void Start()
    {
        currConnectDelay = connectDelayMs;
        userEndPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 8008);
        // vrEndPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 9707);
        // sock.Bind(vrEndPoint);
        Debug.Log("binded");
        // testSend = Encoding.ASCII.GetBytes("AAlmaowhy");
        // sock.SendTo(testSend, userEndPoint);
        Debug.Log("sent");
        // sock.Blocking = false;
        sock.Blocking = true;
    }

    // Update is called once per frame
    void Update()
    {
        if (sock.Poll(10, SelectMode.SelectRead) && sock.Available > 1){
            connected = true;
            // Debug.Log(sock.Available);
            // int len = sock.Receive(readBuff);
            // readBuff[len] = (byte)'\0';
            // Debug.Log(System.Text.Encoding.ASCII.GetString(readBuff));
            Debug.Log("recv");
            byte[] readBuff = new byte[10000];
            sock.Receive(readBuff);
            // readQueue.Enqueue(readBuff);
            decipherOutput(readBuff);
        }
        if (sock.Poll(10, SelectMode.SelectWrite)){
            if (connected && writeQueue.Count > 0){
                Debug.Log("sending...");
                sock.SendTo(writeQueue.Dequeue(), userEndPoint);
            }
            if (!connected && (currConnectDelay < 0)){
                Debug.Log("...");
                // sock.SendTo(Encoding.ASCII.GetBytes("test connection"), userEndPoint);
                byte[] output = {0x01};
                sock.SendTo(output, userEndPoint);
                currConnectDelay = connectDelayMs;
            }
            else if (!connected){
                currConnectDelay -= Mathf.RoundToInt((float)(Time.deltaTime*1000.0));
            }

        }
        if (sock.Poll(10, SelectMode.SelectError)){

        }
    }
    public void writeInput(){

    }
    public void decipherOutput(byte[] input){
        byte command = input[0];
        ArraySegment<byte> payload = new ArraySegment<byte>(input, 1, input.Length-1);
        Debug.Log(command);
        switch(command){
            case 0x01:  // change config

            break;
            case 0x02:  // change vr picture
                Debug.Log("changing view");
                Debug.Log(BitConverter.ToString(input).Replace("-",""));
                renderManager.updateView(System.BitConverter.ToSingle(input, 1)
                , System.BitConverter.ToSingle(input, 5),
                System.BitConverter.ToSingle(input, 9));
            break;
            case 0x03:  // haptic feedback
                
            break;
            case 0x04:  // close connection
            
            break;
            case 0x05:  // open connection
            
            break;
        }
    }
}
