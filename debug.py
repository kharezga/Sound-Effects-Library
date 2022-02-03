import matplotlib.pyplot as plt


class Debug(object):
    def __init__(self, time_domain=0, amp_domain=0):
        """
                Initialize all debugging options.
                :param time_domain: Set x-axis domain
                :param amp_domain: Set y-axis domain

                """
        self.time_domain = time_domain
        self.amp_domain = amp_domain


    def set_time(self, time):
        self.time_domain = time

    def set_amp(self, amp):
        self.amp_domain = amp

    def plot_processed_signal(self, input_audio, output_audio):
        """
        Plot the input and output signal (mostly for debugging purposes).

        :param input_audio
        :param output_audio

        """

        fig, (input, output) = plt.subplots(2)
        input.set_title('Input')
        output.set_title('Output')
        input.plot(input_audio)
        output.plot(output_audio)
        if self.time_domain != 0:
            plt.xlim([0, self.time_domain])
        if self.amp_domain != 0:
            plt.ylim([0, self.time_domain])

        plt.show()

    def measure_time(self, stop=False):
        if stop == False:
            start_time = time.time()
        if stop:
            end = time.time()
            elapsed = int(1000 * (end - start)) * 0.001
            print('Completed in ' + str(elapsed) + ' seconds.')