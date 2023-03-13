# Here we will implement one of the congestion control algorithms learned in lectures called "Reno"   ###
# which will help us deal with network congestion.                                                    ###
class CongestionControl:
    #initialization:
    def __init__(self, ssthresh=65536):
        self.ssthresh = ssthresh
        self.cwnd = 1
        self.dupacks = 0
        self.state = 'slowstart'


### Congestion avoidance "AIMD" – on each loss event, the sending rate is cut in half then grows linearly.  ###
### i.e., if no loss event is experienced the sending rate will increase by 1 each iteration (every RTT).   ###
    def congestion_avoidance(self):
        self.cwnd += 1 / self.cwnd

###  Slow start - increase rate exponentially until first loss event                            ###
###  (congestion window size reaches up to “Slow Start Threshold – "ssthresh" variable).        ###
###  i.e., initially cwnd = 1 MSS then double cwnd for every ACK received (every RTT)           ###
###  until cwnd size reaches up to ssthresh then move to congestion avoidance phase.            ###
    def slow_start(self):
        self.cwnd *= 2


### On each loss event, the sending rate is cut in half then grows linearly.  ###
    def on_packet_loss(self):
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = 1
        self.dupacks = 0
        self.state = 'slowstart'

###  For every ACK received (every RTT) until cwnd size reaches up to ssthresh then move to congestion avoidance phase ###
    def on_packet_acked(self):
        if self.state == 'slowstart':
            if self.cwnd >= self.ssthresh:
                self.state = 'congestion avoidance'
        else:
            self.congestion_avoidance()


### When three duplicate ACKs are received we need to retransmit the lost segment to recover a missing packet.  ###
### The transmission will transmit with a smaller cwnd and if no congestion is experienced cwnd will increase   ###
### according to the AIMD method.                                                                               ###
    def on_duplicate_ack(self):
        self.dupacks += 1
        if self.state == 'slowstart':
            self.slow_start()
        else:
            if self.dupacks == 3:
                self.ssthresh = max(self.cwnd / 2, 2)
                self.cwnd = self.ssthresh + 3
                self.dupacks = 0
                self.state = 'fast recovery'
            else:
                self.congestion_avoidance()

### When timeout occurred, it means that no ACK has arrived, so we will go back to slowstart phase again  ###                                                                            ###
    def on_timeout(self):
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = 1
        self.dupacks = 0
        self.state = 'slowstart'