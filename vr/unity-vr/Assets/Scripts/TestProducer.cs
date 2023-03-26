using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestProducer : MonoBehaviour
{
    // Start is called before the first frame update
    public static float DELAY = 50; // in ms
    private float delayClock;
    public CommPipe commPipe;
    public int num = 0;
    void Start()
    {
        delayClock = DELAY;
    }

    // Update is called once per frame
    void Update()
    {
        // Debug.Log("AAAA");
        if ((delayClock -= Time.deltaTime * 1000) < 0){
            delayClock = DELAY + delayClock;
            // send test data
            // comms.updateHeadPosition(new Vector3(1, 1, 1));
            Debug.Log("sending");
            num++;
            commPipe.writeCurrTime();
            // commPipe.writeData(new Vector3(num, 1, 1));
        }
    }
}
