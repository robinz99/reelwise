def __init__(self, short_type: str, background_video_name: str, background_music_name: str, voiceModule: VoiceModule, short_id="",
                 num_images=None, watermark=None, language: Language = Language.ENGLISH,):
        super().__init__(short_id, short_type, language, voiceModule)
        if not short_id:
            if (num_images):
                self._db_num_images = num_images    


def _generateImageSearchTerms(self):
        self.verifyParameters(captionsTimed=self._db_timed_captions)
        if self._db_num_images:
            self._db_timed_image_searches = gpt_editing.getImageQueryPairs(
                self._db_timed_captions, n=self._db_num_images)

    def _generateImageUrls(self):
        if self._db_timed_image_searches:
            self._db_timed_image_urls = editing_images.getImageUrlsTimed(
                self._db_timed_image_searches)



if self._db_num_images:
                for timing, image_url in self._db_timed_image_urls:
                    videoEditor.addEditingStep(EditingStep.SHOW_IMAGE, {'url': image_url,
                                                                        'set_time_start': timing[0],
                                                                        'set_time_end': timing[1]})
                    


videoEditor.renderVideo(outputPath, logger= self.logger if self.logger is not self.default_logger else None)