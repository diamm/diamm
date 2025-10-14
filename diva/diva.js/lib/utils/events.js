class DivaEvents {
    constructor() {
        this._cache = {};
    }
    publish(topic, args, scope) {
        if (this._cache[topic]) {
            const thisTopic = this._cache[topic];
            if (typeof thisTopic.global !== 'undefined') {
                const thisTopicGlobal = thisTopic.global;
                const globalCount = thisTopicGlobal.length;
                for (let i = 0; i < globalCount; i++) {
                    thisTopicGlobal[i].apply(scope || null, args || []);
                }
            }
            if (scope && typeof scope.getInstanceId !== 'undefined') {
                const instanceID = scope.getInstanceId();
                if (this._cache[topic][instanceID]) {
                    const thisTopicInstance = this._cache[topic][instanceID];
                    const scopedCount = thisTopicInstance.length;
                    for (let j = 0; j < scopedCount; j++) {
                        thisTopicInstance[j].apply(scope, args || []);
                    }
                }
            }
        }
    }
    subscribe(topic, callback, instanceID) {
        if (!this._cache[topic]) {
            this._cache[topic] = {};
        }
        if (typeof instanceID === 'string') {
            if (!this._cache[topic][instanceID]) {
                this._cache[topic][instanceID] = [];
            }
            this._cache[topic][instanceID].push(callback);
        }
        else {
            if (!this._cache[topic].global) {
                this._cache[topic].global = [];
            }
            this._cache[topic].global.push(callback);
        }
        return instanceID ? [topic, callback, instanceID] : [topic, callback];
    }
    unsubscribe(handle, completely) {
        const t = handle[0];
        if (this._cache[t]) {
            let topicArray;
            const instanceID = handle.length === 3 ? handle[2] : 'global';
            topicArray = this._cache[t][instanceID];
            if (!topicArray) {
                return false;
            }
            if (completely) {
                delete this._cache[t][instanceID];
                return topicArray.length > 0;
            }
            let i = topicArray.length;
            while (i--) {
                if (topicArray[i] === handle[1]) {
                    this._cache[t][instanceID].splice(i, 1);
                    return true;
                }
            }
        }
        return false;
    }
    unsubscribeAll(instanceID) {
        if (instanceID) {
            const topics = Object.keys(this._cache);
            let i = topics.length;
            let topic;
            while (i--) {
                topic = topics[i];
                if (typeof this._cache[topic][instanceID] !== 'undefined') {
                    delete this._cache[topic][instanceID];
                }
            }
        }
        else {
            this._cache = {};
        }
    }
}
export let Events = new DivaEvents();
//# sourceMappingURL=events.js.map