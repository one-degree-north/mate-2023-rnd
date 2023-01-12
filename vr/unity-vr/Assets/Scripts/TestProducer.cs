using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestProducer : MonoBehaviour
{
    // Start is called before the first frame update
    public static int DELAY = 1000; // in ms
    private int delayClock;
    public CommPipe commPipe;
    void Start()
    {
        delayClock = DELAY;
    }

    // Update is called once per frame
    void Update()
    {
        if ((delayClock -= Time.deltaTime) < 0){
            delayClock = DELAY + delayClock;
            // send test data
    
        }
    }
}
