#
    # ---------------------------------------------------------------------
    #        Kyutai Client Method - Single Timeout to Avoid ValueError
    # ---------------------------------------------------------------------
    #
    @staticmethod
    def create_kyutai_client(
        *,
        model: TTSModels | str = "tts-1",
        voice: TTSVoices | str = "alloy",
        speed: float = 1.2,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "dummy-key",
    ) -> TTS:
        """
        Create a TTS client pointing to a local Kyutai TTS endpoint,
        which is OpenAI-compatible.
        """
        kyutai_client = openai.AsyncClient(
            max_retries=0,
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),  # Single default - longer for TTS model loading
                follow_redirects=True,
                limits=httpx.Limits(
                    max_connections=50,
                    max_keepalive_connections=50,
                    keepalive_expiry=120,
                ),
            ),
        )

        return TTS(
            model=model,
            voice=voice,
            speed=speed,
            client=kyutai_client,
        )

