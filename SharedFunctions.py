def InsertByVar(objList, newObj): #insert element in list based on time
    #find relevant position where the obj should be placed
    i = 0
    for i, obj in enumerate(objList):
        if obj.time >= newObj.time: #new element is worse than this element
            break #break and use the i index
        elif i == len(objList) - 1: #this is the highest time
            i += 1 #raise the index so it gets placed at the end

    #insert the new obj in the correct position
    objList.insert(i, newObj)
    return objList
