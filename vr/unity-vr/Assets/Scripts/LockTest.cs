using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;

public class LockTest : MonoBehaviour
{
    // Start is called before the first frame update
    private Mutex mut;
    void Start()
    {
        mut = new Mutex(false, "test");
        bool acquired = mut.WaitOne();
        Debug.Log(acquired);
        acquired = mut.WaitOne(1000);
        Debug.Log(acquired);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
