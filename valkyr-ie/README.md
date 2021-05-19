# ner4soft meets valkyr-ie

Donwload the last release at: https://github.com/oeg-upm/valkyr-ie-gate/releases

Gazetteers and rules for Ner4soft are in their corresponding folders

Check processes.conf to add or modify gazetters and rules

## To execute

```
java -jar valkyr-ie-gate-1.0.jar      
```

You can specify the port:

```
java -jar -Dserver.port=8084 valkyr-ie-gate-1.0.jar      
```


Example of use
```
curl -X POST "http://localhost:8080/processText" -H "accept: application/json;charset=UTF-8" -H "Content-Type: application/json;charset=UTF-8" -d "{ \"text\": \"Lets search for torch==1.5.0\"}"
```

