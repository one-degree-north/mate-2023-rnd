using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestProducer : MonoBehaviour
{
    // Start is called before the first frame update
    public static float DELAY = 1; // in ms
    private float delayClock;
    public CommPipe commPipe;
    public Communications comms;
    public int num = 0;
    void Start()
    {
        delayClock = DELAY;
    }

    // Update is called once per frame
    void Update()
    {
        if ((delayClock -= Time.deltaTime * 1000) < 0){
            delayClock = DELAY + delayClock;
            // send test data
            // comms.updateHeadPosition(new Vector3(1, 1, 1));
            num++;
            commPipe.writeData(new Vector3(num, 1, 1));
        }
    }
}
